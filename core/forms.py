from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from .models import CustomUser, HealthWorker, Patient, Appointment


class WorkerSignupForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    phone_number = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(
            initial='NG',
            country_attrs={'class': 'phone_country'},
            number_attrs={'class': 'phone_num'}
        ),
        required=False
    )
    position = forms.ChoiceField(choices=CustomUser.POSITIONS, required=True,
                                 widget=forms.Select(attrs={'class': 'select-input'}))
    is_worker = forms.BooleanField(
        required=True,
        label='I agree',
        widget=forms.CheckboxInput(attrs={'class': 'check-input'})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'password1', 'password2', 'position', 'is_worker']
        widget = {
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput()
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.Meta.model.objects.filter(email=email).exists():
            raise ValidationError('This email is already in use.')
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if self.Meta.model.objects.filter(phone_number=phone_number).exists():
            raise ValidationError('This phone number is already in use.')
        return phone_number

    # def clean_position(self):
    #     position = self.cleaned_data.get('position')
    #     if not position:
    #         raise ValidationError('Please enter a position.')
    #     return position

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def clean(self):
        cleaned_data = super().clean()
        is_worker = cleaned_data.get('is_worker')
        if not is_worker:
            raise ValidationError("Please check here")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            worker, created = HealthWorker.objects.get_or_create(user=user)
            worker.save()
        return user


class WorkerLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput())

    # # remove the autofocus attribute on the username field
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['username'].widget.attrs.pop('autofocus', None)


class PatientSignupForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    phone_number = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(
            initial='NG',
            country_attrs={'class': 'phone_country'},
            number_attrs={'class': 'phone_num'}
        ),
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'password1', 'password2']
        widget = {
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput()
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.Meta.model.objects.filter(email=email).exists():
            raise ValidationError('This email is already in use.')
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if self.Meta.model.objects.filter(phone_number=phone_number).exists():
            raise ValidationError('This phone number is already in use.')
        return phone_number

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            patient, created = Patient.objects.get_or_create(user=user)
            patient.save()
        return user


class PatientLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput())

    # # remove the autofocus attribute on the username field
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['username'].widget.attrs.pop('autofocus', None)


class MedicalInfoForm(forms.ModelForm):
    class Meta:
        model = Patient
        is_diabetic = forms.BooleanField(label='Are you Diabetic?')
        has_allergy = forms.BooleanField(label='Do you have anAllergy?')
        has_fever = forms.BooleanField(label='Have you experienced Fever?')
        fields = ['blood_group', 'age', 'gender', 'height', 'weight', 'is_diabetic', 'has_allergy', 'has_fever']


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['worker', 'patient', 'date', 'time']
