from django.urls import path
from .views import (WorkerSignupView, WorkerLoginView, PatientSignupView,
                    PatientLoginView, HomePageView, WorkerDashboardView,
                    LogoutView, PatientDashboardView, PatientInformationView,
                    WorkerViewPatientView, HealthStatisticView, BookAppointmentView
                    )


app_name = 'core'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('worker/signup/', WorkerSignupView.as_view(), name='worker_signup'),
    path('worker/login/', WorkerLoginView.as_view(), name='worker_login'),
    path('patient/signup/', PatientSignupView.as_view(), name='patient_signup'),
    path('patient/login/', PatientLoginView.as_view(), name='patient_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('<int:user_id>/worker/dashboard/', WorkerDashboardView.as_view(), name='worker_dashboard'),
    path('<int:user_id>/statistic/', HealthStatisticView.as_view(), name='health_statistic'),
    path('<int:user_id>/patient/dashboard', PatientDashboardView.as_view(), name='patient_dashboard'),
    path('<int:user_id>/patient/information/', PatientInformationView.as_view(), name='patient_information'),
    path('<int:user_id>/worker/patient/detail/<int:pk>/', WorkerViewPatientView.as_view(), name='patient_detail'),
    path('<int:user_id>/appointment/book/', BookAppointmentView.as_view(), name='book_appointment'),
    # path('<int:user_id>/appointment/status/', AcceptRejectAppointmentView.as_view(), name='status'),
]
