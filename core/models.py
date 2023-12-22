from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.


class CustomUser(AbstractUser):
    POSITIONS = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('pharmacist', 'Pharmacist'),
    )
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('username'), null=True, blank=True, max_length=100)
    phone_number = PhoneNumberField(blank=True, unique=True, null=True, verbose_name="Phone Number",
                                    error_messages={'unique': 'Phone number already used'})
    position = models.CharField(max_length=32, null=True, blank=True, choices=POSITIONS)
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
        return reverse('core:worker_detail', args=[self.user.pk])


class Patient(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='patient')
    blood_group = models.CharField(max_length=10, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    # malaria = models.BooleanField(default=False)
    is_diabetic = models.BooleanField(default=False)
    has_allergy = models.BooleanField(default=False)
    has_fever = models.BooleanField(default=False)
    worker = models.ManyToManyField(HealthWorker, blank=True, related_name='patients')

    class Meta:
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'

    def __str__(self):
        return self.user.email

    def get_absolute_url(self):
        return reverse('core:patient_detail', args=[self.user.pk])


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    worker = models.ForeignKey(HealthWorker, on_delete=models.CASCADE, related_name='appointments')
    patient = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'

    def __str__(self):
        return f'{self.worker.user.email} - {self.patient.user.email} - {self.date} {self.time}'

