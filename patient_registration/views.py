from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    return render(request, 'patient_registration/dashboard.html', {'title': 'Dashboard'})


@login_required
def add_patient(request):
    return render(request, 'patient_registration/add-patient.html', {'title': 'Add'})


@login_required
def add_service(request):
    return render(request, 'patient_registration/add-service.html', {'title': 'Add'})


@login_required
def add_appointment(request):
    return render(request, 'patient_registration/add-appointment.html', {'title': 'Add'})


@login_required
def appointment(request):
    return render(request, 'patient_registration/appointments.html', {'title': 'Appointments'})


@login_required
def invoice(request):
    return render(request, 'patient_registration/invoice.html', {'title': 'Invoice'})
