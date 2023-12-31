from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth.models import Group
from django.urls import reverse_lazy

from core.models import HealthWorker, Patient


class CustomAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        user = super(CustomAccountAdapter, self).save_user(request, user, form, commit=False)
        user.phone_number = form.cleaned_data['phone_number']
        user.is_worker = form.cleaned_data['is_worker']
        user.agreement = form.cleaned_data['agreement']

        if commit:
            user.save()
            if user.is_worker:
                health_worker_user, created = HealthWorker.objects.get_or_create(user=user)
                health_worker_user.save()

                health_worker_group, created = Group.objects.get_or_create(name='Health Workers')
                user.groups.add(health_worker_group)
            else:
                patient_user, created = Patient.objects.get_or_create(user=user)
                patient_user.save()

                patient_group, created = Group.objects.get_or_create(name='Patients')
                user.groups.add(patient_group)

        return user

    def get_signup_redirect_url(self, request):
        if request.user.is_worker:
            path = reverse_lazy('core:worker_dashboard', kwargs={'user_id': request.user.id})
            return path
        else:
            path = reverse_lazy('core:patient_dashboard', kwargs={'user_id': request.user.id})
            return path

    def get_login_redirect_url(self, request):
        if request.user.is_worker:
            path = reverse_lazy('core:worker_dashboard', kwargs={'user_id': request.user.id})
            return path
        else:
            path = reverse_lazy('core:patient_dashboard', kwargs={'user_id': request.user.id})
            return path

