from collections import defaultdict

from strawberry.dataloader import DataLoader

from core import models


def _by_pk(model):
    """Relation plusieurs-à-un : N objets par clé primaire en 1 requête."""
    async def load(keys: list[int]):
        objs = {o.pk: o async for o in model.objects.filter(pk__in=keys)}
        return [objs.get(k) for k in keys]
    return DataLoader(load_fn=load)


def _children(model, fk_name):
    """Relation un-à-plusieurs : les enfants de N parents en 1 requête."""
    attname = f"{fk_name}_id"

    async def load(keys: list[int]):
        groups = defaultdict(list)
        qs = model.objects.filter(**{f"{attname}__in": keys}).order_by("pk")
        async for obj in qs:
            groups[getattr(obj, attname)].append(obj)
        return [groups.get(k, []) for k in keys]
    return DataLoader(load_fn=load)


def make_loaders() -> dict:
    """À appeler UNE FOIS PAR REQUÊTE HTTP."""
    return {
        "organizer": _by_pk(models.Organizer),
        "venue": _by_pk(models.Venue),
        "participant": _by_pk(models.Participant),
        "event": _by_pk(models.Event),
        "reservation": _by_pk(models.Reservation),
        "events_by_organizer": _children(models.Event, "organizer"),
        "events_by_venue": _children(models.Event, "venue"),
        "reservations_by_event": _children(models.Reservation, "event"),
        "reservations_by_participant": _children(models.Reservation, "participant"),
        "tickets_by_reservation": _children(models.Ticket, "reservation"),
    }