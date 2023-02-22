from django.db import models

from datetime import datetime

from django.contrib.auth.models import User

# Create your models here.
# Creating different choices for the courses
COURSE_CHOICES = (
    ("Course One", "Course One"),
    ("Course Two", "Course Two"),
    ("Course Three", "Course Three"),
    ("Course Four", "Course Four")
)

# Handeling time choices
TIME_CHOICES = (
    ("08h00", "08h00"),
    ("09h00", "09h00"),
    ("10h00", "10h00"),
    ("11h00", "11h00"),
    ("13h00", "13h00"),
    ("14h00", "14h00"),
    ("15h00", "15h00"),
    ("16h00", "16h00"),
    ("17h00", "17h00")
)

# Appointment() will handle the rdv by collecting 5 data :
# - The user booking this RDV
# - The selected course
# - The day of the RDV
# - The time selected for the Course
# - The date and time off the reservation by the User


class Appointment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    service = models.CharField(
        max_length=50, choices=COURSE_CHOICES, default="Course One")
    day = models.DateField(default=datetime.now)
    time = models.CharField(
        max_length=10, choices=TIME_CHOICES, default="08h00")
    time_ordered = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return f"{self.user.username} | day: {self.day} | time: {self.time}"
