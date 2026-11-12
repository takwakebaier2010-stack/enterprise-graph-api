
import strawberry
import strawberry_django
from strawberry import auto
from strawberry import relay
from datetime import datetime

from django.db.models import QuerySet
from strawberry_django.relay import DjangoCursorConnection

from core import models


# TYPES GRAPHQL

@strawberry_django.type(models.Organizer)
class OrganizerType:
    id: auto
    name: auto
    country: auto


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
    organizer: "OrganizerType"
    venue: "VenueType"


@strawberry_django.type(models.Reservation)
class ReservationType:
    id: auto
    status: auto
    created_at: auto
    event: "EventType"
    participant: "ParticipantType"
    tickets: list["TicketType"]


@strawberry_django.type(models.Ticket)
class TicketType:
    id: auto
    seat: auto
    price: auto
    checked_in: auto
    reservation: "ReservationType"


# QUERIES

@strawberry.type
class Query:

    # List queries
    organizers: list[OrganizerType] = strawberry_django.field()
    participants: list[ParticipantType] = strawberry_django.field()
    reservations: list[ReservationType] = strawberry_django.field()
    tickets: list[TicketType] = strawberry_django.field()
    venues: list[VenueType] = strawberry_django.field()

    @strawberry.field
    def events(
        self,
        title: str | None = None,
        organizer_id: int | None = None,
        venue_id: int | None = None,
        order_by: str = "starts_at"
    ) -> list[EventType]:

        queryset = models.Event.objects.all()

        # Filter by title
        if title:
            queryset = queryset.filter(title__icontains=title.strip())

        # Filter by organizer
        if organizer_id is not None:
            queryset = queryset.filter(organizer_id=organizer_id)

        # Filter by venue
        if venue_id is not None:
            queryset = queryset.filter(venue_id=venue_id)

        # Validate ordering field
        allowed_ordering = [
            "title", "-title",
            "starts_at", "-starts_at"
        ]

        if order_by not in allowed_ordering:
            raise ValueError("Invalid ordering field")

        return list(queryset.order_by(order_by))

    # Detail queries using Django integer IDs

    @strawberry.field
    def organizer(self, id: int) -> OrganizerType | None:
        return models.Organizer.objects.filter(pk=id).first()

    @strawberry.field
    def event(self, id: int) -> EventType | None:
        return models.Event.objects.filter(pk=id).first()

    @strawberry.field
    def participant(self, id: int) -> ParticipantType | None:
        return models.Participant.objects.filter(pk=id).first()

    @strawberry.field
    def reservation(self, id: int) -> ReservationType | None:
        return models.Reservation.objects.filter(pk=id).first()

    @strawberry.field
    def ticket(self, id: int) -> TicketType | None:
        return models.Ticket.objects.filter(pk=id).first()

    @strawberry.field
    def venue(self, id: int) -> VenueType | None:
        return models.Venue.objects.filter(pk=id).first()

    # Relay cursor pagination

    @strawberry_django.connection(
        DjangoCursorConnection[EventType]
    )
    def events_paginated(self) -> QuerySet[models.Event]:
        return models.Event.objects.all().order_by("id")


# INPUT TYPES

@strawberry.input
class EventInput:
    title: str
    starts_at: datetime
    organizer_id: int
    venue_id: int


@strawberry.input
class ReservationInput:
    event_id: int
    participant_id: int
    status: str | None = None


# MUTATIONS

@strawberry.type
class Mutation:

    # Create Event

    @strawberry.mutation
    def create_event(self, input: EventInput) -> EventType:

        # Validate title
        if not input.title.strip():
            raise ValueError("Event title cannot be empty")

        # Check organizer
        organizer = models.Organizer.objects.filter(
            pk=input.organizer_id
        ).first()

        if organizer is None:
            raise ValueError("Organizer not found")

        # Check venue
        venue = models.Venue.objects.filter(
            pk=input.venue_id
        ).first()

        if venue is None:
            raise ValueError("Venue not found")

        return models.Event.objects.create(
            title=input.title.strip(),
            starts_at=input.starts_at,
            organizer=organizer,
            venue=venue
        )

    # Create Reservation

    @strawberry.mutation
    def create_reservation(
        self,
        input: ReservationInput
    ) -> ReservationType:

        # Check event
        event = models.Event.objects.filter(
            pk=input.event_id
        ).first()

        if event is None:
            raise ValueError("Event not found")

        # Check participant
        participant = models.Participant.objects.filter(
            pk=input.participant_id
        ).first()

        if participant is None:
            raise ValueError("Participant not found")

        # Normalize and validate status
        status = input.status

        if status is None:
            status = models.Reservation.Status.PENDING
        else:
            status = status.strip().lower()

        if status not in models.Reservation.Status.values:
            raise ValueError("Invalid reservation status")

        return models.Reservation.objects.create(
            event=event,
            participant=participant,
            status=status
        )
    
# GRAPHQL SCHEMA

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)
