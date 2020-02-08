from django import forms
from .models import Invoice, Service, Appointment


class InvoiceCreateForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['doctor', 'deposit']


class ServiceCreateForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['treatment', 'tooth', 'laboratory_name', 'amount', 'description']


class AppointmentCreateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'note']
        widgets = {
            'date': forms.DateTimeInput(attrs={'class': 'datetimepicker'})
        }


class PatientAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'date', 'note']
        widgets = {
            'date': forms.DateTimeInput(attrs={'class': 'datetimepicker'})
        }
