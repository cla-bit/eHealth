from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import CustomUser, HealthWorker, Patient, Appointment
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


@receiver(post_save, sender=Appointment)
def send_appointment_email(sender, instance, created, **kwargs):
    if created:
        # Send an email to the worker
        send_mail(
            'New Appointment Request',
            f'Patient {instance.patient.user.username} has requested an appointment with you on {instance.date}'
            f' at {instance.time}.\n Please accept or reject the request.\n Thank you!\n'
            f'You can reply to {instance.patient.user.username} at {instance.patient.user.email}',
            'from@example.com',
            [instance.worker.user.email],
            fail_silently=False,
        )

