import strawberry
import strawberry_django
from strawberry import auto

from core import models


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
class EventType:
    id: auto
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

@strawberry_django.type(models.Ticket)
class TicketType:
    id: auto
    seat: auto
    price: auto
    checked_in: auto
    reservation: "ReservationType"

@strawberry.type
class Query:
    organizers: list[OrganizerType] = strawberry_django.field()
    events: list[EventType] = strawberry_django.field()
    participants: list[ParticipantType] = strawberry_django.field()
    reservations: list[ReservationType] = strawberry_django.field()
    tickets: list[TicketType] = strawberry_django.field()
    venues: list[VenueType] = strawberry_django.field()


schema = strawberry.Schema(query=Query)