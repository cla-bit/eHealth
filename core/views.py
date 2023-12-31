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
from .filters import PatientFilter, WorkerPositionFilter
from .forms import MedicalInfoForm, AppointmentForm, WorkerInfoForm
from .models import HealthWorker, Patient, CustomUser, Appointment


class HomePageView(TemplateView):
    template_name = 'home/home.html'


@method_decorator(login_required, name='dispatch')
class WorkerDashboardView(View):
    template_name = 'home/worker_dashboard.html'

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        worker_user = get_object_or_404(CustomUser, pk=user_id)
        worker = get_object_or_404(HealthWorker, user=worker_user)

        appointments = Appointment.objects.filter(worker=worker)
        accepted_count = appointments.filter(status='accepted').count()
        rejected_count = appointments.filter(status='rejected').count()
        pending_count = appointments.filter(status='pending').count()

        total_appointments = appointments.count()

        patients = Patient.objects.all()
        patient_filter = PatientFilter(request.GET, queryset=patients)
        patients = patient_filter.qs

        logout_url = reverse('account_logout')

        return render(request, self.template_name, {'worker': worker, 'logout_url': logout_url,
                                                    'patients': patients, 'filter': patient_filter,
                                                    'total_appointments': total_appointments,
                                                    'accepted_count': accepted_count,
                                                    'rejected_count': rejected_count,
                                                    'pending_count': pending_count})


@method_decorator(login_required, name='dispatch')
class WorkerInformationView(UpdateView):
    model = HealthWorker
    form_class = WorkerInfoForm
    template_name = 'home/worker_information.html'

    def get_object(self, queryset=None):
        # Ensure that the patient being updated belongs to the current user
        return self.model.objects.get(user=self.request.user)

    # def get_form(self, form_class=None):
    #     form = super(WorkerInformationView, self).get_form(form_class)
    #     form.fields['position'].widget.attrs['disabled'] = True
    #     form.fields['department'].widget.attrs['readonly'] = True
    #     return form

    def form_valid(self, form):
        form.instance.user = self.request.user  # Assign the current user to the patient
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('core:worker_dashboard', kwargs={'user_id': self.request.user.pk})


@method_decorator(login_required, name='dispatch')
class WorkerViewPatientView(DetailView):
    model = Patient
    template_name = 'home/view_patient.html'
    context_object_name = 'patient'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        worker_user = self.kwargs.get('user_id')
        patient_id = self.get_object()

        context['worker'] = worker_user
        context['patient'] = patient_id
        return context


@method_decorator(login_required, name='dispatch')
class HealthStatisticView(View):
    template_name = 'home/health_statistic.html'

    def get(self, request, *args, **kwargs):
        patient_count = Patient.objects.count()
        diabetic_patients = Patient.objects.filter(diabetic=True).count()
        fever_patients = Patient.objects.filter(fever=True).count()
        allergy_patients = Patient.objects.filter(allergy=True).count()
        malaria_patients = Patient.objects.filter(malaria=True).count()

        # chart data
        labels = ['Patients', 'Diabetic', 'Fever', 'Allergy', 'Malaria']
        data = [patient_count, diabetic_patients, fever_patients, allergy_patients, malaria_patients]

        context = {
            'labels': labels,
            'data': data
        }

        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class PatientDashboardView(View):
    template_name = 'home/patient_dashboard.html'

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        patient_user = get_object_or_404(CustomUser, pk=user_id)
        patient = get_object_or_404(Patient, user=patient_user)

        workers = HealthWorker.objects.all()
        worker_filter = WorkerPositionFilter(request.GET, queryset=workers)
        workers = worker_filter.qs
        logout_url = reverse('account_logout')

        return render(request, self.template_name, {
            'patient': patient, 'logout_url': logout_url, **patient.__dict__, 'workers': workers,
            'filter': worker_filter})


@method_decorator(login_required, name='dispatch')
class PatientInformationView(UpdateView):
    model = Patient
    form_class = MedicalInfoForm
    template_name = 'home/patient_information.html'

    def get_object(self, queryset=None):
        # Ensure that the patient being updated belongs to the current user
        return self.model.objects.get(user=self.request.user)

    # def get_form(self, form_class=None):
    #     form = super(PatientInformationView, self).get_form(form_class)
    #     form.fields['age'].widget.attrs['readonly'] = True
    #     form.fields['gender'].widget.attrs['disabled'] = True
    #     form.fields['blood_group'].widget.attrs['disabled'] = True
    #     form.fields['genotype'].widget.attrs['disabled'] = True
    #     form.fields['height'].widget.attrs['readonly'] = True
    #     form.fields['weight'].widget.attrs['readonly'] = True
    #     return form

    def form_valid(self, form):
        form.instance.user = self.request.user  # Assign the current user to the patient
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('core:patient_dashboard', kwargs={'user_id': self.request.user.pk})


@method_decorator(login_required, name='dispatch')
class BookAppointmentView(View):
    template_name = 'home/appointment.html'

    def get(self, request, *args, **kwargs):
        # Assuming 'worker_id' is passed in the URL
        patient_id = self.kwargs.get('user_id')
        patient = get_object_or_404(Patient, user=patient_id)
        workers = HealthWorker.objects.all()
        form = AppointmentForm(initial={'patient': patient})
        return render(request, self.template_name, {'form': form, 'workers': workers})

    def post(self, request, *args, **kwargs):
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            patient = get_object_or_404(Patient, user=request.user)
            appointment.patient = patient
            appointment.status = 'pending'
            appointment.save()

            messages.success(request, 'Appointment booked successfully.')

            return redirect('core:book_appointment', user_id=request.user.id)

        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class AcceptRejectAppointmentView( View):
    template_name = 'home/status.html'

    def get(self, request, *args, **kwargs):
        worker_id = self.kwargs.get('pk')
        worker = get_object_or_404(HealthWorker, user=worker_id)
        appointments = Appointment.objects.filter(worker=worker).filter(status='pending')

        return render(request, self.template_name, {'appointment': appointments})

    def post(self, request, *args, **kwargs):
        # Assuming 'appointment_id', 'action' are passed in the URL and 'worker_id' is passed in the context
        appointment_id = request.POST.get('item_id')
        worker_id = self.kwargs.get('user_id')
        action = request.POST.get('action')
        appointment = get_object_or_404(Appointment, id=appointment_id)

        if action == 'accept':
            appointment.accept_appointment()
        elif action == 'reject':
            appointment.reject_appointment()

        return redirect('core:worker_dashboard', user_id=request.user.id)
