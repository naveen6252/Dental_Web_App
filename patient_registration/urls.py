from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='patient-registration-home'),
    path('add-patient/', views.add_patient, name='patient-registration-add-patient'),
    path('add-service/', views.add_service, name='patient-registration-add-service'),
    path('add-appointment/', views.add_appointment, name='patient-registration-add-appointment'),
    path('appointments/', views.appointment, name='patient-registration-appointments'),
    path('invoice/', views.invoice, name='patient-registration-invoice'),
]