from django.contrib import admin
from .models import Doctor, Patient, Service, Invoice, Appointment, Treatment, ExpenseType, Expense

# Register your models here.
admin.site.register([Doctor, Patient, Service, Invoice, Appointment, Treatment, ExpenseType, Expense])
