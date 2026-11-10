import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.models import (
    Event,
    Organizer,
    Participant,
    Reservation,
    Ticket,
    Venue,
)

N_ORGANIZERS = 5
N_VENUES = 10
N_PARTICIPANTS = 200
EVENTS_PER_ORGANIZER = 10
RESERVATIONS_PER_EVENT = 20
MAX_TICKETS_PER_RESERVATION = 3

CITIES = ["Tunis", "Sfax", "Sousse", "Bizerte", "Nabeul", "Gabès", "Kairouan"]
COUNTRIES = ["Tunisia", "France", "Morocco", "Algeria"]
EVENT_TYPES = ["Concert", "Conference", "Festival", "Workshop", "Match", "Expo"]


class Command(BaseCommand):
    help = "Fill the database with reproducible test data for the N+1 demo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing data before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["clear"]:
            Ticket.objects.all().delete()
            Reservation.objects.all().delete()
            Event.objects.all().delete()
            Participant.objects.all().delete()
            Venue.objects.all().delete()
            Organizer.objects.all().delete()
            self.stdout.write("Existing data deleted.")
        elif Organizer.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Data already exists. Use --clear to reset and reseed."
                )
            )
            return

        random.seed(42)  # same data on every machine

        organizers = Organizer.objects.bulk_create(
            Organizer(
                name=f"Organizer {i}",
                country=random.choice(COUNTRIES),
            )
            for i in range(1, N_ORGANIZERS + 1)
        )

        venues = Venue.objects.bulk_create(
            Venue(
                name=f"Venue {i}",
                city=random.choice(CITIES),
                capacity=random.choice([200, 500, 1000, 5000]),
            )
            for i in range(1, N_VENUES + 1)
        )

        participants = Participant.objects.bulk_create(
            Participant(
                full_name=f"Participant {i}",
                email=f"participant{i}@example.com",
            )
            for i in range(1, N_PARTICIPANTS + 1)
        )

        now = timezone.now()
        events = Event.objects.bulk_create(
            Event(
                organizer=organizer,
                venue=random.choice(venues),
                title=f"{random.choice(EVENT_TYPES)} {organizer.pk}-{n}",
                starts_at=now + timedelta(days=random.randint(1, 180)),
            )
            for organizer in organizers
            for n in range(1, EVENTS_PER_ORGANIZER + 1)
        )

        statuses = [s for s, _ in Reservation.Status.choices]
        reservations = Reservation.objects.bulk_create(
            Reservation(
                event=event,
                participant=participant,
                status=random.choice(statuses),
            )
            for event in events
            for participant in random.sample(participants, RESERVATIONS_PER_EVENT)
        )

        Ticket.objects.bulk_create(
            Ticket(
                reservation=reservation,
                seat=f"{random.choice('ABCDEF')}{random.randint(1, 60)}",
                price=Decimal(random.choice([15, 25, 40, 60, 90])),
                checked_in=random.random() < 0.3,
            )
            for reservation in reservations
            for _ in range(random.randint(1, MAX_TICKETS_PER_RESERVATION))
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Seed done: "
                f"{Organizer.objects.count()} organizers, "
                f"{Venue.objects.count()} venues, "
                f"{Participant.objects.count()} participants, "
                f"{Event.objects.count()} events, "
                f"{Reservation.objects.count()} reservations, "
                f"{Ticket.objects.count()} tickets."
            )
        )