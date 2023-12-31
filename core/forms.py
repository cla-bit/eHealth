from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget, RegionalPhoneNumberWidget
from .models import CustomUser, HealthWorker, Patient, Appointment


class CustomUserRegistrationForm(SignupForm):
    email = forms.EmailField(required=True, label='Email Address')
    username = forms.CharField(max_length=100, required=True, label='Username')
    phone_number = PhoneNumberField(widget=RegionalPhoneNumberWidget(region='NG'),
                                    required=True, label='Phone Number')
    is_worker = forms.BooleanField(required=False, label='I am a Licensed Health Practitioner')
    agreement = forms.BooleanField(required=True, label='I agree to the terms and conditions')

    def save(self, request):
        user = super(CustomUserRegistrationForm, self).save(request)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        user.phone_number = self.cleaned_data['phone_number']
        user.agreement = self.cleaned_data['agreement']
        user.is_worker = self.cleaned_data['is_worker']

        # Save the user to the CustomerCustomUser model
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

        user.save()
        return user


class WorkerInfoForm(forms.ModelForm):
    class Meta:
        model = HealthWorker
        position = forms.ChoiceField(choices=HealthWorker.POSITIONS, required=True,
                                      widget=forms.Select(attrs={'class': 'form-control'}))
        department = forms.CharField(label='Department', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
        fields = ['position', 'department']


class MedicalInfoForm(forms.ModelForm):
    class Meta:
        model = Patient
        diabetic = forms.BooleanField(label='Are you Diabetic?')
        allergy = forms.BooleanField(label='Do you have anAllergy?')
        fever = forms.BooleanField(label='Have you experienced Fever?')
        fields = ['blood_group', 'age', 'gender', 'genotype', 'height', 'weight', 'malaria', 'diabetic', 'allergy', 'fever']


class AppointmentForm(forms.ModelForm):
    worker = forms.ModelChoiceField(queryset=HealthWorker.objects.all(), label='Select a Health Worker')
    patient = forms.CharField(label='Patient Name')
    date = forms.DateField(label='Date', widget=forms.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(label='Time', widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Appointment
        fields = ['worker', 'patient', 'date', 'time']
