from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test.client import RequestFactory
from .views import WorkerSignupView, WorkerLoginView, PatientSignupView, PatientLoginView, WorkerDashboardView, PatientDashboardView

class WorkerSignupViewTest(TestCase):
    def test_worker_signup_view_get(self):
        response = self.client.get(reverse('worker_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forms/health-signup.html')

    def test_worker_signup_view_post_valid_data(self):
        data = {'username': 'test@example.com', 'password': 'password', 'is_worker': True}
        response = self.client.post(reverse('worker_signup'), data)
        self.assertEqual(response.status_code, 302)  # Should redirect after successful signup

    def test_worker_signup_view_post_invalid_data(self):
        data = {'username': 'test@example.com', 'password': 'password', 'is_worker': False}
        response = self.client.post(reverse('worker_signup'), data)
        self.assertEqual(response.status_code, 200)  # Should stay on the signup page
        self.assertFormError(response, 'form', 'is_worker', 'This field is required')

    # Add more test cases as needed

class WorkerLoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test@example.com', password='password', is_worker=True)

    def test_worker_login_view_get(self):
        response = self.client.get(reverse('worker_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forms/health-login.html')

    def test_worker_login_view_post_valid_data(self):
        data = {'username': 'test@example.com', 'password': 'password'}
        response = self.client.post(reverse('worker_login'), data)
        self.assertEqual(response.status_code, 302)  # Should redirect after successful login

    def test_worker_login_view_post_invalid_data(self):
        data = {'username': 'test@example.com', 'password': 'wrong_password'}
        response = self.client.post(reverse('worker_login'), data)
        self.assertEqual(response.status_code, 200)  # Should stay on the login page
        self.assertContains(response, 'Invalid Email or password')

    # Add more test cases as needed

# Similar tests for PatientSignupView, PatientLoginView, WorkerDashboardView, and PatientDashboardView
