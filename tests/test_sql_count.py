"""
Vérification CI : le nombre de requêtes SQL du schéma DataLoader est CONSTANT (O(1)),
quelle que soit la taille des données, alors que le schéma naïf explose (N+1).

Requête testée (4 niveaux) : organizers -> events -> reservations -> tickets
"""
import asyncio
from datetime import timedelta

import pytest
from asgiref.sync import sync_to_async
from django.db import connections
from django.db.backends.utils import CursorWrapper
from django.utils import timezone

from core import models
from core.loaders import make_loaders
from core.schema import schema
from core.schema_optimized import schema_optimized

QUERY = """
{ organizers { name events { title reservations { status tickets { seat price } } } } }
"""

# 1 requête par niveau : organizers, events, reservations, tickets
EXPECTED_DATALOADER_QUERIES = 4


@pytest.fixture
def sql_counter(monkeypatch):
    """Compte chaque requête SQL envoyée à la base (tous threads confondus)."""
    counter = {"n": 0}
    original = CursorWrapper.execute

    def counting_execute(self, sql, params=None):
        counter["n"] += 1
        return original(self, sql, params)

    monkeypatch.setattr(CursorWrapper, "execute", counting_execute)
    return counter


def build_dataset(n_organizers, events_per_org, reservations_per_event, tickets_per_reservation):
    venue = models.Venue.objects.create(name="Venue", city="Tunis", capacity=100)
    participant = models.Participant.objects.create(
        full_name="Test", email=f"t{models.Participant.objects.count()}@example.com"
    )
    now = timezone.now()
    for o in range(n_organizers):
        organizer = models.Organizer.objects.create(name=f"Org {o}", country="TN")
        for e in range(events_per_org):
            event = models.Event.objects.create(
                organizer=organizer, venue=venue, title=f"Event {o}-{e}",
                starts_at=now + timedelta(days=e),
            )
            for _ in range(reservations_per_event):
                reservation = models.Reservation.objects.create(
                    event=event, participant=participant
                )
                for t in range(tickets_per_reservation):
                    models.Ticket.objects.create(
                        reservation=reservation, seat=f"A{t}", price=10
                    )


async def run_dataloader_query():
    try:
        return await schema_optimized.execute(
            QUERY, context_value={"loaders": make_loaders()}
        )
    finally:
        # ferme la connexion ouverte par le thread async (évite l'avertissement
        # « base de données en cours d'utilisation » à la fin des tests)
        await sync_to_async(connections.close_all)()


def count_dataloader_queries(counter):
    counter["n"] = 0
    result = asyncio.run(run_dataloader_query())
    assert result.errors is None, result.errors
    return counter["n"], result.data


def count_naive_queries(counter):
    counter["n"] = 0
    result = schema.execute_sync(QUERY)
    assert result.errors is None, result.errors
    return counter["n"], result.data


@pytest.mark.django_db(transaction=True)
def test_dataloader_uses_constant_number_of_queries(sql_counter):
    # Petit jeu de données : 2 + 6 + 12 + 24 lignes
    build_dataset(2, 3, 2, 2)
    small, _ = count_dataloader_queries(sql_counter)

    # Jeu de données 10x plus gros : on ajoute 8 organisateurs, 6 événements, ...
    build_dataset(8, 6, 4, 3)
    large, _ = count_dataloader_queries(sql_counter)

    assert small == EXPECTED_DATALOADER_QUERIES
    assert large == EXPECTED_DATALOADER_QUERIES
    assert small == large  # O(1) : indépendant de la taille des données


@pytest.mark.django_db(transaction=True)
def test_naive_schema_suffers_from_n_plus_one(sql_counter):
    build_dataset(3, 4, 3, 2)  # 3 organisateurs, 12 événements, 36 réservations
    naive, _ = count_naive_queries(sql_counter)

    # 1 (organizers) + 3 (events) + 12 (reservations) + 36 (tickets) = 52
    assert naive > 4 * EXPECTED_DATALOADER_QUERIES
    assert naive == 1 + 3 + 12 + 36


@pytest.mark.django_db(transaction=True)
def test_dataloader_and_naive_return_identical_results(sql_counter):
    build_dataset(3, 4, 3, 2)
    _, naive_data = count_naive_queries(sql_counter)
    _, optimized_data = count_dataloader_queries(sql_counter)

    def canon(x):
        if isinstance(x, dict):
            return {k: canon(v) for k, v in sorted(x.items())}
        if isinstance(x, list):
            return sorted((canon(i) for i in x), key=repr)
        return x

    assert canon(naive_data) == canon(optimized_data)


@pytest.mark.django_db(transaction=True)
def test_optimized_schema_supports_relay_event_pagination():
    build_dataset(1, 3, 0, 0)

    async def execute(query):
        try:
            return await schema_optimized.execute(
                query, context_value={"loaders": make_loaders()}
            )
        finally:
            await sync_to_async(connections.close_all)()

    first_page = asyncio.run(execute("""
        { eventsPaginated(first: 2) {
            edges { cursor node { title } }
            pageInfo { hasNextPage endCursor }
        } }
    """))
    assert first_page.errors is None, first_page.errors
    page = first_page.data["eventsPaginated"]
    assert len(page["edges"]) == 2
    assert page["pageInfo"]["hasNextPage"] is True

    second_page = asyncio.run(execute(f"""
        {{ eventsPaginated(first: 2, after: "{page['pageInfo']['endCursor']}") {{
            edges {{ node {{ title }} }}
            pageInfo {{ hasNextPage }}
        }} }}
    """))
    assert second_page.errors is None, second_page.errors
    next_page = second_page.data["eventsPaginated"]
    assert len(next_page["edges"]) == 1
    assert next_page["pageInfo"]["hasNextPage"] is False


@pytest.mark.django_db(transaction=True)
def test_optimized_schema_supports_event_and_reservation_mutations():
    build_dataset(1, 0, 0, 0)
    organizer = models.Organizer.objects.first()
    venue = models.Venue.objects.first()
    participant = models.Participant.objects.first()

    async def execute(query):
        try:
            return await schema_optimized.execute(
                query, context_value={"loaders": make_loaders()}
            )
        finally:
            await sync_to_async(connections.close_all)()

    create_event = asyncio.run(execute(f'''
        mutation {{ createEvent(input: {{
            title: "  Created through optimized schema  "
            startsAt: "2026-11-20T12:00:00+00:00"
            organizerId: {organizer.pk}
            venueId: {venue.pk}
        }}) {{ id title }} }}
    '''))
    assert create_event.errors is None, create_event.errors
    event = create_event.data["createEvent"]
    assert event["title"] == "Created through optimized schema"
    event_model = models.Event.objects.get(title=event["title"])

    create_reservation = asyncio.run(execute(f'''
        mutation {{ createReservation(input: {{
            eventId: {event_model.pk}
            participantId: {participant.pk}
        }}) {{ status }} }}
    '''))
    assert create_reservation.errors is None, create_reservation.errors
    assert create_reservation.data["createReservation"]["status"] == "pending"
