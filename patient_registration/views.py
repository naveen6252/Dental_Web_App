from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def home(request):
    return render(request, 'patient_registration/dashboard.html', {'title': 'Dashboard'})


def add_patient(request):
    return render(request, 'patient_registration/add-patient.html', {'title': 'Add'})


def add_service(request):
    return render(request, 'patient_registration/add-service.html', {'title': 'Add'})


def add_appointment(request):
    return render(request, 'patient_registration/add-appointment.html', {'title': 'Add'})


def appointment(request):
    return render(request, 'patient_registration/appointments.html', {'title': 'Appointments'})


def invoice(request):
    return render(request, 'patient_registration/invoice.html', {'title': 'Invoice'})
