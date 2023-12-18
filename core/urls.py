from django.urls import path
from .views import (WorkerSignupView, WorkerLoginView, PatientSignupView,
                    PatientLoginView, HomePageView, WorkerDashboardView,
                    LogoutView, PatientDashboardView, PatientInformationView)


app_name= 'core'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('worker/signup/', WorkerSignupView.as_view(), name='worker_signup'),
    path('worker/login/', WorkerLoginView.as_view(), name='worker_login'),
    path('patient/signup/', PatientSignupView.as_view(), name='patient_signup'),
    path('patient/login/', PatientLoginView.as_view(), name='patient_login'),
    path('<int:user_id>/worker/dashboard/', WorkerDashboardView.as_view(), name='worker_dashboard'),
    path('<int:user_id>/patient/dashboard', PatientDashboardView.as_view(), name='patient_dashboard'),
    path('<int:user_id>/patient/information/', PatientInformationView.as_view(), name='patient_information'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
