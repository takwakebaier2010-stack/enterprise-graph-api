import strawberry
import strawberry_django
from strawberry import auto, relay
from strawberry.types import Info

from core import models


def loaders(info: Info) -> dict:
    return info.context["loaders"]


@strawberry_django.type(models.Organizer)
class OrganizerType:
    id: auto
    name: auto
    country: auto

    @strawberry.field
    async def events(self, info: Info) -> list["EventType"]:
        return await loaders(info)["events_by_organizer"].load(self.pk)


@strawberry_django.type(models.Venue)
class VenueType:
    id: auto
    name: auto
    city: auto
    capacity: auto


@strawberry_django.type(models.Participant)
class ParticipantType:
    id: auto
    full_name: auto
    email: auto


@strawberry_django.type(models.Event)
class EventType(relay.Node):
    id: relay.NodeID[int]
    title: auto
    starts_at: auto

    @strawberry.field
    async def organizer(self, info: Info) -> "OrganizerType":
        return await loaders(info)["organizer"].load(self.organizer_id)

    @strawberry.field
    async def venue(self, info: Info) -> "VenueType":
        return await loaders(info)["venue"].load(self.venue_id)

    @strawberry.field
    async def reservations(self, info: Info) -> list["ReservationType"]:
        return await loaders(info)["reservations_by_event"].load(self.pk)


@strawberry_django.type(models.Reservation)
class ReservationType:
    id: auto
    status: auto
    created_at: auto

    @strawberry.field
    async def event(self, info: Info) -> "EventType":
        return await loaders(info)["event"].load(self.event_id)

    @strawberry.field
    async def participant(self, info: Info) -> "ParticipantType":
        return await loaders(info)["participant"].load(self.participant_id)

    @strawberry.field
    async def tickets(self, info: Info) -> list["TicketType"]:
        return await loaders(info)["tickets_by_reservation"].load(self.pk)


@strawberry_django.type(models.Ticket)
class TicketType:
    id: auto
    seat: auto
    price: auto
    checked_in: auto

    @strawberry.field
    async def reservation(self, info: Info) -> "ReservationType":
        return await loaders(info)["reservation"].load(self.reservation_id)


ALLOWED_ORDERING = {"title", "-title", "starts_at", "-starts_at"}


async def _all(model):
    return [obj async for obj in model.objects.order_by("pk")]


@strawberry.type
class Query:
    @strawberry.field
    async def organizers(self) -> list[OrganizerType]:
        return await _all(models.Organizer)

    @strawberry.field
    async def participants(self) -> list[ParticipantType]:
        return await _all(models.Participant)

    @strawberry.field
    async def venues(self) -> list[VenueType]:
        return await _all(models.Venue)

    @strawberry.field
    async def reservations(self) -> list[ReservationType]:
        return await _all(models.Reservation)

    @strawberry.field
    async def tickets(self) -> list[TicketType]:
        return await _all(models.Ticket)

    @strawberry.field
    async def events(
        self,
        title: str | None = None,
        organizer_id: int | None = None,
        venue_id: int | None = None,
        order_by: str = "starts_at",
    ) -> list[EventType]:
        if order_by not in ALLOWED_ORDERING:
            raise ValueError("Invalid ordering field")

        qs = models.Event.objects.all()
        if title:
            qs = qs.filter(title__icontains=title.strip())
        if organizer_id is not None:
            qs = qs.filter(organizer_id=organizer_id)
        if venue_id is not None:
            qs = qs.filter(venue_id=venue_id)

        return [e async for e in qs.order_by(order_by)]


schema_optimized = strawberry.Schema(query=Query)