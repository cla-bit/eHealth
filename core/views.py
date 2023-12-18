from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import View, ListView, DetailView, FormView, TemplateView, UpdateView, CreateView
from django.views.generic.detail import SingleObjectMixin
from .filters import PatientFilter
from .forms import WorkerSignupForm, WorkerLoginForm, PatientSignupForm, PatientLoginForm, MedicalInfoForm, \
    AppointmentForm
from .models import HealthWorker, Patient, CustomUser, Appointment


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

        worker = HealthWorker.objects.get(user=worker_user)
        patients = Patient.objects.all()
        logout_url = reverse('core:logout')
        patient_filter = PatientFilter(request.GET, queryset=patients)
        patients = patient_filter.qs

        return render(request, self.template_name, {'worker': worker, 'logout_url': logout_url,
                                                    'patients': patients, 'filter': patient_filter})


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

        patient = Patient.objects.get(user=patient_user)
        logout_url = reverse('core:logout')

        return render(request, self.template_name, {
            'patient': patient, 'logout_url': logout_url, **patient.__dict__})


@method_decorator(login_required, name='dispatch')
class PatientInformationView(UpdateView):
    model = Patient
    form_class = MedicalInfoForm
    template_name = 'home/patient_information.html'

    def get_object(self, queryset=None):
        # Ensure that the patient being updated belongs to the current user
        return self.model.objects.get(user=self.request.user)

    def form_valid(self, form):
        form.instance.user = self.request.user  # Assign the current user to the patient
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('core:patient_dashboard', kwargs={'user_id': self.request.user.id})


@method_decorator(login_required, name='dispatch')
class BookAppointmentView(View):
    template_name = 'home/book_appointment.html'

    def get(self, request, *args, **kwargs):
        form = AppointmentForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = AppointmentForm(request.POST)
        if form.is_valid():
            # Assuming 'worker_id' is passed in the URL
            worker_id = kwargs.get('worker_id')
            try:
                worker = HealthWorker.objects.get(id=worker_id)
            except HealthWorker.DoesNotExist:
                return render(request, 'error.html', {'error_message': 'Health Worker not found'})

            patient = request.user.patient
            appointment = form.save(commit=False)
            appointment.worker = worker
            appointment.patient = patient
            appointment.save()

            # Send an email to the worker
            send_mail(
                'New Appointment Request',
                f'Patient {patient.user.email} has requested an appointment with you on {appointment.date} at {appointment.time}.',
                'from@example.com',
                [worker.user.email],
                fail_silently=False,
            )

            return redirect('core:patient_dashboard', user_id=request.user.id)

        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class AcceptRejectAppointmentView(View):
    def post(self, request, *args, **kwargs):
        # Assuming 'appointment_id', 'action' are passed in the URL and 'worker_id' is passed in the context
        appointment_id = kwargs.get('appointment_id')
        action = request.POST.get('action')
        worker_id = request.context['worker_id']

        try:
            appointment = Appointment.objects.get(id=appointment_id)
            worker = HealthWorker.objects.get(id=worker_id)
        except (Appointment.DoesNotExist, HealthWorker.DoesNotExist):
            return render(request, 'error.html', {'error_message': 'Appointment or Health Worker not found'})

        if action == 'accept':
            appointment.status = 'accepted'
        elif action == 'reject':
            appointment.status = 'rejected'
        else:
            return render(request, 'error.html', {'error_message': 'Invalid action'})

        appointment.save()

        return redirect('core:worker_dashboard', user_id=worker.user.id)
