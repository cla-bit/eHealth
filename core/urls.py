from django.urls import path
from .views import (HomePageView, WorkerDashboardView, WorkerViewPatientView, HealthStatisticView, WorkerInformationView,
                    PatientDashboardView, PatientInformationView, BookAppointmentView, AcceptRejectAppointmentView
                    )


app_name = 'core'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('worker/<int:user_id>/dashboard/', WorkerDashboardView.as_view(), name='worker_dashboard'),
    path('worker/<int:user_id>/patient/detail/<int:pk>/', WorkerViewPatientView.as_view(), name='patient_detail'),
    path('worker/<int:user_id>/update/', WorkerInformationView.as_view(), name='worker_information'),
    path('statistic/', HealthStatisticView.as_view(), name='health_statistic'),
    path('patient/<int:user_id>/dashboard', PatientDashboardView.as_view(), name='patient_dashboard'),
    path('patient/<int:user_id>/information/', PatientInformationView.as_view(), name='patient_information'),
    path('<int:user_id>/appointment/book/', BookAppointmentView.as_view(), name='book_appointment'),
    path('<int:pk>/appointment/status/', AcceptRejectAppointmentView.as_view(), name='status'),
]
