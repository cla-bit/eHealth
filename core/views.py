from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import View, ListView, DetailView, FormView, TemplateView
from django.views.generic.detail import SingleObjectMixin

from .forms import WorkerSignupForm, WorkerLoginForm, PatientSignupForm, PatientLoginForm
from .models import HealthWorker, Patient, CustomUser


class HomePageView(TemplateView):
    template_name = 'home/home.html'


class WorkerSignupView(View):
    def get(self, request):
        form = WorkerSignupForm()
        return render(request, 'forms/health-signup.html', {'form': form})

    def post(self, request):
        form = WorkerSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            is_worker = form.cleaned_data.get('is_worker')
            user.save()
            if is_worker:
                worker, created = HealthWorker.objects.get_or_create(user=user)
                worker.save()
            login(request, user)
            return redirect(reverse('core:worker_dashboard', kwargs={'user_id': user.id}))
        messages
        return render(request, 'forms/health-signup.html', {'form': form})


class WorkerLoginView(View):
    def get(self, request):
        form = WorkerLoginForm()
        return render(request, 'forms/health-login.html', {'form': form})

    def post(self, request):
        form = WorkerLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None and user.is_worker:
                login(request, user)
                return redirect(reverse('core:worker_dashboard', kwargs={'user_id': user.id}))
        messages.error(request, "Invalid Email or password.")
        return render(request, 'forms/health-login.html', {'form': form})


class PatientSignupView(View):
    def get(self, request):
        form = PatientSignupForm()
        return render(request, 'forms/patient-signup.html', {'form': form})

    def post(self, request):
        form = PatientSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            patient, created = Patient.objects.get_or_create(user=user)
            patient.save()
            login(request, user)
            return redirect(reverse('core:patient_dashboard', kwargs={'user_id': user.id}))
        return render(request, 'forms/health-signup.html', {'form': form})


class PatientLoginView(View):
    def get(self, request):
        form = PatientLoginForm()
        return render(request, 'forms/patient-login.html', {'form': form})

    def post(self, request):
        form = PatientLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('core:patient_dashboard', kwargs={'user_id': user.id}))
        messages.error(request, "Invalid Email or password.")
        return render(request, 'forms/patient-login.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class LogoutView(View):
    template_name = 'forms/logout.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('core:home')


@method_decorator(login_required, name='dispatch')
class WorkerDashboardView(View):
    template_name = 'home/worker_dashboard.html'

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        try:
            worker_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            # Handle the case where the user with the given ID does not exist
            return render(request, 'error.html', {'error_message': 'User not found'})

        worker = worker_user.worker  # Assuming the related name is 'health_worker'
        logout_url = reverse('core:logout')

        return render(request, self.template_name, {'worker': worker, 'logout_url': logout_url})


@method_decorator(login_required, name='dispatch')
class PatientDashboardView(View):
    template_name = 'home/patient_dashboard.html'

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        try:
            patient_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            # Handle the case where the user with the given ID does not exist
            return render(request, 'error.html', {'error_message': 'User not found'})

        patient = patient_user.patient  # Assuming the related name is 'health_worker'
        logout_url = reverse('core:logout')

        return render(request, self.template_name, {'worker': patient, 'logout_url': logout_url})
