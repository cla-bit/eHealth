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
        subject = f'Appointment Request with {instance.patient.user.first_name}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [instance.health_worker.user.email]
        html_message = render_to_string('email/appointment_request.html', {
            'appointment': instance
            # 'patient': instance.patient
            # 'worker': instance.worker
            # 'date': instance.date
            # 'time': instance.time
            # 'status': instance.status

        })

        send_mail(
            subject,
            strip_tags(html_message),
            from_email,
            to_email,
            html_message=html_message
            # fail_silently=False
            # html_message=html_message
        )

        # patient = instance.patient
        # worker = instance.worker
        # if patient and worker:
        #     appointment_date = instance.date.strftime('%Y-%m-%d')
