from django.db import models


class Organizer(models.Model):
    name = models.CharField(max_length=120)
    country = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return self.name


class Venue(models.Model):
    name = models.CharField(max_length=120)
    city = models.CharField(max_length=80)
    capacity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Participant(models.Model):
    full_name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.full_name


class Event(models.Model):
    organizer = models.ForeignKey(
        Organizer, related_name="events", on_delete=models.CASCADE
    )
    venue = models.ForeignKey(
        Venue, related_name="events", on_delete=models.PROTECT
    )
    title = models.CharField(max_length=200)
    starts_at = models.DateTimeField()

    def __str__(self):
        return self.title


class Reservation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    event = models.ForeignKey(
        Event, related_name="reservations", on_delete=models.CASCADE
    )
    participant = models.ForeignKey(
        Participant, related_name="reservations", on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Ticket(models.Model):
    reservation = models.ForeignKey(
        Reservation, related_name="tickets", on_delete=models.CASCADE
    )
    seat = models.CharField(max_length=20, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    checked_in = models.BooleanField(default=False)