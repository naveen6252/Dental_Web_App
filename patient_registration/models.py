from django.db import models
from django.core.validators import MinLengthValidator
from django.utils import timezone
from django.urls import reverse


class Doctor(models.Model):
    name = models.CharField(max_length=50)
    contact = models.CharField(max_length=15)
    designation = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('patient-registration-doctors')


class Patient(models.Model):
    gender_choices = [
        (0, 'Male'),
        (1, 'Female'),
        (2, 'Other')
    ]
    patient_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=15, validators=[MinLengthValidator(6)])
    age = models.IntegerField()
    sex = models.IntegerField(choices=gender_choices)
    address = models.TextField()
    register_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.patient_id)

    def get_absolute_url(self):
        return reverse('patient-registration-add-invoice-service', kwargs={'p_id': self.patient_id})


class Invoice(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    deposit = models.IntegerField(default=0)
    invoice_date = models.DateTimeField(default=timezone.now)
    note = models.TextField(blank=True)

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        return reverse('patient-registration-view-slip', kwargs={'pk': self.patient.id})


class Service(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    treatment = models.CharField(max_length=50)
    tooth = models.CharField(max_length=50, blank=True)
    service_date = models.DateTimeField(default=timezone.now)
    laboratory_name = models.CharField(max_length=50, blank=True)
    amount = models.IntegerField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.treatment

    def get_absolute_url(self):
        return reverse('patient-registration-add-more-service', kwargs={'inv_id': self.invoice.id})


class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateTimeField()
    note = models.TextField(blank=True)

    def __str__(self):
        return '{0} {1}'.format(self.doctor, self.date)

    def get_absolute_url(self):
        return reverse('patient-registration-home')
