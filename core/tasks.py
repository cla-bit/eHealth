from celery import shared_task
from django.core.mail import EmailMessage, BadHeaderError
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging
from .models import CustomUser

logger = logging.getLogger(__name__)


# send email to new registered users
@shared_task
def send_email_to_new_users(user_email):
    try:
        template = render_to_string('account/messages/email_confirmed.txt',
                                    {'email': user_email})
        html_message = strip_tags(template)
        email = EmailMessage(
            subject='Email Confirmation on Registration',
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[user_email]
        )

        email.fail_silently = False
        email.content_subtype = 'html'
        email.send()
    except BadHeaderError as e:
        logger.error(f'Error sending email: {e}')
        raise e


@shared_task
def send_email_to_logged_in_users(user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        template = render_to_string('account/messages/logged_in.txt',
                                    {'user': user})
        html_message = strip_tags(template)
        email = EmailMessage(
            subject='Login Confirmation',
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email]
        )

        email.fail_silently = False
        email.content_subtype = 'html'
        email.send()
    except CustomUser.DoesNotExist as e:
        logger.error(f'Error getting user: {e}')
    except BadHeaderError as e:
        logger.error(f'Error sending email: {e}')
        raise e


@shared_task
def send_email_to_logged_out_users(user_email):
    try:
        template = render_to_string('account/messages/logged_out.txt',
                                    {'email': user_email})
        html_message = strip_tags(template)
        email = EmailMessage(
            subject='Logout Confirmation',
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[user_email]
        )

        email.fail_silently = False
        email.content_subtype = 'html'
        email.send()
    except BadHeaderError as e:
        logger.error(f'Error sending email: {e}')
        raise e
