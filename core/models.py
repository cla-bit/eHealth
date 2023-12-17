from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.


class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('username'), null=True, blank=True, max_length=100)
    phone_number = PhoneNumberField(blank=True, unique=True, null=True, verbose_name="Phone Number",
                                    error_messages={'unique': 'Phone number already used'})
    position = models.CharField(max_length=32, null=True, blank=True)
    is_worker = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']

    def __str__(self):
        return self.email


class HealthWorker(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='worker')
    department = models.CharField(max_length=200, null=True)

    class Meta:
        verbose_name = 'Health Worker'
        verbose_name_plural = 'Health Workers'

    def __str__(self):
        return self.user.email

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        group, _ = Group.objects.get_or_create(name='Health Worker')
        self.user.groups.add(group)

    def delete(self, *args, **kwargs):
        self.user.groups.clear()
        self.user.user_permissions.clear()
        super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('core:worker_dashboard', args=[self.user.id])


class Patient(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='patient')
    blood_group = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'

    def __str__(self):
        return self.user.email
