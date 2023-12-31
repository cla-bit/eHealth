from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from .models import CustomUser, Appointment
from .tasks import send_email_to_new_users, send_email_to_logged_in_users, send_email_to_logged_out_users
from allauth.account.signals import user_signed_up, user_logged_in, user_logged_out
from .forms import CustomUserRegistrationForm


@receiver(user_signed_up)
def user_signed_up_handler(sender, request, user, **kwargs):
    if user and request:
        send_email_to_new_users.delay(user.email)


# @receiver(post_save, sender=CustomUser)
# def user_add_group_handler(sender, instance, created, **kwargs):
#     if created and instance.is_worker:
#         health_workers_group, created = Group.objects.get_or_create(name='Health Workers')
#         instance.groups.add(health_workers_group)
#     else:
#         patients_group, created = Group.objects.get_or_create(name='Patients')
#         instance.groups.add(patients_group)


@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    if user and request:
        send_email_to_logged_in_users.delay(user.id)


@receiver(user_logged_out, sender=CustomUser)
def user_logged_out_handler(sender, request, user, **kwargs):
    if user and request:
        send_email_to_logged_out_users.delay(user.email)


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
