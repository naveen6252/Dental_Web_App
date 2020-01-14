from django.db import models
from django.utils import timezone


class Doctor(models.Model):
    name = models.CharField(max_length=50)
    contact = models.CharField(max_length=15)
    designation = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Patient(models.Model):
    gender_choices = (('M', 'Male'), ('F', 'Female'), ('O', 'Other'))
    patient_id = models.IntegerField()
    name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=15)
    age = models.IntegerField()
    sex = models.CharField(max_length=1, choices=gender_choices)
    address = models.TextField()

    def __str__(self):
        return str(self.patient_id)


class Invoice(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    total_amount = models.IntegerField(default=0)
    deposit = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)


class Service(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    treatment = models.CharField(max_length=50)
    tooth = models.CharField(max_length=50, blank=True)
    date = models.DateTimeField(default=timezone.now)
    laboratory_name = models.CharField(max_length=50, blank=True)
    amount = models.IntegerField()

    def __str__(self):
        return self.treatment


class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateTimeField()

    def __str__(self):
        return '{0} {1}'.format(self.doctor, self.date)
