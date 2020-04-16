from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from .models import Patient, Doctor, Appointment, Service, Invoice, Treatment, Expense
from datetime import timedelta
from django.utils import timezone
from social_django.utils import load_strategy
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from .social_google_credentials import Credentials
import requests
import json
import csv
from .forms import InvoiceCreateForm, ServiceCreateForm, AppointmentCreateForm, PatientAppointmentForm
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    DeleteView,
    UpdateView
)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def home(request):
    today = timezone.now()
    month_first_date = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_first_date = (month_first_date - timedelta(days=1)).replace(day=1)
    last_month_last_date = month_first_date - timedelta(microseconds=1)
    total_patients = Patient.objects.count()
    curr_month_patients = Patient.objects.filter(register_date__gte=month_first_date, register_date__lte=today).count()
    mtd_sales = Invoice.objects.filter(
        invoice_date__gte=month_first_date, invoice_date__lte=today).aggregate(Sum('deposit'))['deposit__sum']
    last_month_sale = Invoice.objects.filter(
        invoice_date__gte=last_month_first_date, invoice_date__lte=last_month_last_date).aggregate(
        Sum('deposit'))['deposit__sum']

    total_appointments = Appointment.objects.count()
    completed_appointments = Appointment.objects.filter(date__lte=timezone.now())
    revenue = Invoice.objects.aggregate(Sum('deposit'))['deposit__sum']
    service_amount = Service.objects.aggregate(Sum('amount'))['amount__sum']
    due = service_amount - revenue
    total_invoices = Invoice.objects.count()

    mom_deposit = Invoice.objects.annotate(month=TruncMonth('invoice_date')).values('month').annotate(
        deposit=Sum('deposit')).values('month', 'deposit')

    mom_amount = Service.objects.annotate(month=TruncMonth('service_date')).values('month').annotate(
        amount=Sum('amount')).values('month', 'amount')

    deposit_by_doctor = Invoice.objects.values('service__treatment').annotate(deposit=Sum('deposit'))
    amount_by_doctor = Service.objects.values('treatment').annotate(amount=Sum('amount'))

    appointment_by_doctor = Appointment.objects.values('doctor').annotate(appointment=Count('patient'))

    return render(request, 'patient_registration/dashboard.html', {'title': 'Dashboard'})


class PatientListView(LoginRequiredMixin, ListView):
    model = Patient

    def get_context_data(self, **kwargs):
        context = super(PatientListView, self).get_context_data(**kwargs)

        context['title'] = 'Patient'
        return context


class PatientDeleteView(LoginRequiredMixin, DeleteView):
    model = Patient

    def get_success_url(self):
        return reverse('patient-registration-patients')

    def get_context_data(self, **kwargs):
        context = super(PatientDeleteView, self).get_context_data(**kwargs)
        context['title'] = 'Patient Delete'
        return context


class PatientDetailView(LoginRequiredMixin, DetailView):
    model = Patient

    def get_context_data(self, **kwargs):
        context = super(PatientDetailView, self).get_context_data(**kwargs)
        patient = self.get_object()
        context['services'] = Service.objects.filter(invoice__patient=patient).order_by('-service_date')
        context['invoices'] = patient.invoice_set.order_by('-invoice_date')
        context['title'] = 'Patient'
        return context


class PatientCreateView(LoginRequiredMixin, CreateView):
    model = Patient
    fields = ['name', 'image', 'mobile', 'sex', 'birth_date', 'address']

    def form_valid(self, form):
        number = Patient.objects.filter(register_date__date=timezone.now().date()).count() + 1
        number = '0' + str(number) if number < 10 else str(number)
        p_id = timezone.now().strftime('%Y%m%d') + number
        form.instance.patient_id = int(p_id)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(PatientCreateView, self).get_context_data(**kwargs)
        context['title'] = 'Patient Registration'
        return context


class TreatmentCreateView(LoginRequiredMixin, CreateView):
    model = Treatment
    fields = ['treatment']

    def get_context_data(self, **kwargs):
        context = super(TreatmentCreateView, self).get_context_data(**kwargs)
        context['title'] = 'Patient Registration'
        return context


class PatientUpdateView(LoginRequiredMixin, UpdateView):
    model = Patient
    fields = ['patient_id', 'name', 'image', 'mobile', 'sex', 'birth_date', 'address']

    def get_context_data(self, **kwargs):
        context = super(PatientUpdateView, self).get_context_data(**kwargs)
        context['title'] = 'Patient Registration'
        return context


@login_required
def add_invoice_service(request, p_id):
    patient = Patient.objects.get(patient_id=p_id)
    if request.method == 'POST':
        inv_form = InvoiceCreateForm(request.POST)
        serv_form = ServiceCreateForm(request.POST)
        if inv_form.is_valid() and serv_form.is_valid():
            inv = inv_form.save(commit=False)
            inv.patient = patient
            inv.doctor = Doctor.objects.get(id=request.POST.get('doctor'))
            inv.save()
            serv = serv_form.save(commit=False)
            serv.invoice = inv
            serv.save()
            return redirect('patient-registration-add-more-service', inv_id=inv.id)
    else:
        inv_form = InvoiceCreateForm()
        serv_form = ServiceCreateForm()

    context = {'title': 'Patient Registration', 'inv_form': inv_form, 'serv_form': serv_form, 'patient': patient}

    return render(request, 'patient_registration/add-service.html', context)


class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    fields = ['doctor', 'deposit']

    def form_valid(self, form):
        patient = Patient.objects.get(patient_id=self.kwargs.get('p_id'))
        form.instance.patient = patient
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(InvoiceCreateView, self).get_context_data(**kwargs)
        context['patient'] = Patient.objects.get(patient_id=self.kwargs.get('p_id'))
        context['title'] = 'Patient Registration'
        return context


class ServiceCreateView(LoginRequiredMixin, CreateView):
    model = Service
    fields = ['treatment', 'tooth', 'laboratory_name', 'amount', 'description']

    def form_valid(self, form):
        invoice = Invoice.objects.get(id=self.kwargs.get('inv_id'))
        form.instance.invoice = invoice
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        invoice = Invoice.objects.get(id=self.kwargs.get('inv_id'))
        context = super(ServiceCreateView, self).get_context_data(**kwargs)
        context['invoice'] = invoice
        context['title'] = 'Patient Registration'
        return context


class DoctorCreateView(LoginRequiredMixin, CreateView):
    model = Doctor
    fields = ['name', 'contact', 'designation', 'logo', 'address']

    def get_context_data(self, **kwargs):
        context = super(DoctorCreateView, self).get_context_data(**kwargs)
        context['title'] = 'Doctor'
        return context


class DoctorUpdateView(LoginRequiredMixin, UpdateView):
    model = Doctor
    fields = ['name', 'contact', 'designation', 'logo', 'address']

    def get_context_data(self, **kwargs):
        context = super(DoctorUpdateView, self).get_context_data(**kwargs)
        context['title'] = 'Doctor'
        return context


class DoctorListView(LoginRequiredMixin, ListView):
    model = Doctor

    def get_context_data(self, **kwargs):
        context = super(DoctorListView, self).get_context_data(**kwargs)
        context['title'] = 'Doctor'
        return context


class DoctorDeleteView(LoginRequiredMixin, DeleteView):
    model = Doctor

    def get_success_url(self):
        return reverse('patient-registration-doctors')

    def get_context_data(self, **kwargs):
        context = super(DoctorDeleteView, self).get_context_data(**kwargs)
        context['title'] = 'Doctor Delete'
        return context


class AppointmentCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentCreateForm

    def form_valid(self, form):
        patient = Patient.objects.get(patient_id=self.kwargs.get('p_id'))
        form.instance.patient = patient
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(AppointmentCreateView, self).get_context_data(**kwargs)
        context['title'] = 'Appointment'
        return context


class AppointmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Appointment
    fields = ['doctor', 'patient', 'date', 'note']

    def get_context_data(self, **kwargs):
        context = super(AppointmentUpdateView, self).get_context_data(**kwargs)
        context['title'] = 'Appointment'
        return context


class AppointmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Appointment

    def get_success_url(self):
        return reverse('patient-registration-view-appointment', kwargs={'doc_id': self.get_object().doctor.id})

    def get_context_data(self, **kwargs):
        context = super(AppointmentDeleteView, self).get_context_data(**kwargs)
        context['title'] = 'Appointment - Delete'
        return context


@login_required
def appointments(request, doc_id):
    doctor = Doctor.objects.get(id=doc_id)
    if request.method == 'POST':
        appointment_form = PatientAppointmentForm(request.POST)
        if appointment_form.is_valid():
            appointment = appointment_form.save(commit=False)
            appointment.doctor = doctor
            appointment.save()

            return redirect('patient-registration-view-appointment', doc_id=doc_id)

    else:
        appointment_form = PatientAppointmentForm()

    appointments_array = []
    current_appointments = Appointment.objects.filter(doctor__id=doc_id)
    for appointment in current_appointments:
        start = appointment.date
        end = start + timedelta(minutes=30)
        appointments_array.append(
            {'title': str(appointment.patient.patient_id) + '-' + appointment.patient.name,
             'start': start.astimezone().strftime('%Y-%m-%dT%H:%M:%S'),
             'end': end.astimezone().strftime('%Y-%m-%dT%H:%M:%S'),
             'note': appointment.note, 'appointment_id': appointment.id, 'allDay': False}
        )

    all_appointments = json.dumps(appointments_array)

    next_appointments = current_appointments.filter(date__gte=timezone.now()).order_by('date')
    context = {'appointments_json': all_appointments, 'title': 'Appointment', 'doctor': doctor,
               'form': appointment_form,
               'next_appointments': next_appointments, 'appointments': current_appointments}
    return render(request, 'patient_registration/appointments.html', context)


@login_required
def doctor_select(request):
    doctors = Doctor.objects.all()
    context = {'title': 'Appointment', 'doctors': doctors}
    return render(request, 'patient_registration/doctor_select.html', context)


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice

    def get_context_data(self, **kwargs):
        context = super(InvoiceDetailView, self).get_context_data(**kwargs)
        context['title'] = 'Invoice'
        bill_total = self.get_object().service_set.aggregate(Sum('amount'))['amount__sum']
        bill_total = bill_total if bill_total else 0
        context['bill_total'] = bill_total
        context['bill_due'] = bill_total - self.get_object().deposit
        return context


class InvoiceSlipView(LoginRequiredMixin, DetailView):
    model = Patient
    template_name = 'patient_registration/invoice_slip.html'

    def get_context_data(self, **kwargs):
        context = super(InvoiceSlipView, self).get_context_data(**kwargs)
        context['title'] = 'Invoice'
        return context


@login_required
def export_data(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="PatientData' + timezone.now().astimezone().strftime(
        '%Y%m%d_%H%M%S') + '.csv"'
    writer = csv.writer(response)

    writer.writerow(['Patient_ID', 'Patient Name', 'Mobile', 'Age', 'Sex', 'Address', 'Registered Date', 'Doctor Name',
                     'Invoice ID', 'Invoice Date', 'Deposit', 'Invoice Note', 'Service ID', 'Treatment', 'Tooth',
                     'Treatment Date', 'Laboratory', 'Treatment Amount', 'Treatment Description'])

    services = Service.objects.all()
    for service in services:
        invoice = service.invoice
        patient = invoice.patient
        doctor = invoice.doctor
        row = [patient.patient_id, patient.name, patient.mobile, patient.age, patient.sex, patient.address,
               patient.register_date, doctor.name, invoice.id, invoice.invoice_date, invoice.deposit, invoice.note,
               service.id, service.treatment.treatment, service.tooth, service.service_date, service.laboratory_name,
               service.amount, service.description]
        writer.writerow(row)

    invoices = Invoice.objects.filter(service__isnull=True)
    for invoice in invoices:
        patient = invoice.patient
        doctor = invoice.doctor
        row = [patient.patient_id, patient.name, patient.mobile, patient.age, patient.sex, patient.address,
               patient.register_date, doctor.name, invoice.id, invoice.invoice_date, invoice.deposit, invoice.note, '',
               '', '', '', '', '', '']
        writer.writerow(row)
    return response


@login_required
def birth_days(request):
    patients = Patient.objects.all()
    today_date = timezone.now()
    tomorrow_date = timezone.now() + timedelta(days=1)
    today_birth_day = patients.filter(birth_date__day=today_date.day, birth_date__month=today_date.month)
    tomorrow_birth_day = patients.filter(birth_date__day=tomorrow_date.day, birth_date__month=tomorrow_date.month)
    context = {'title': 'BirthDays', 'today_patient': today_birth_day, 'tomorrow_patient': tomorrow_birth_day}
    return render(request, 'patient_registration/patient_birth_days.html', context)


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    fields = ['type', 'amount', 'date']

    def get_context_data(self, **kwargs):
        context = super(ExpenseCreateView, self).get_context_data(**kwargs)
        context['title'] = 'Expense'
        return context


class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    model = Expense
    fields = ['type', 'amount', 'date']

    def get_context_data(self, **kwargs):
        context = super(ExpenseUpdateView, self).get_context_data(**kwargs)
        context['title'] = 'Expense'
        return context


class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense

    def get_context_data(self, **kwargs):
        context = super(ExpenseListView, self).get_context_data(**kwargs)

        context['title'] = 'Expense'
        return context


@login_required
def export_contacts(request):
    social = request.user.social_auth.get(provider='google-oauth2')

    service = build('people', 'v1', credentials=Credentials(social))
    people = service.people()
    temp_people = people.connections().list(resourceName='people/me', personFields='names').execute()

    temp_page_token = temp_people.get("nextPageToken")
    connection_list = temp_people["connections"]

    while temp_page_token:
        temp_people = people.connections().list(resourceName='people/me', pageToken=temp_page_token,
                                                personFields='names').execute()
        connection_list += temp_people["connections"]
        temp_page_token = temp_people.get("nextPageToken")

    existing_patient_contact = []

    for val in connection_list:
        if val.get('names'):
            for name in val.get('names'):
                if name.get("honorificPrefix"):
                    existing_patient_contact.append(name.get("honorificPrefix"))

    for patient in Patient.objects.all():
        if str(patient.patient_id) not in existing_patient_contact:
            people.createContact(
                body={
                    "names": [
                        {"displayName": patient.name, "givenName": patient.name,
                         "honorificPrefix": str(patient.patient_id)}],
                    "phoneNumbers": [
                        {
                            'value': patient.mobile
                        }
                    ],
                    'organizations': [{
                        'name': 'Harbor-dental',
                        'title': 'Patient'
                    }]
                }
            ).execute()

    return render(request, 'patient_registration/export-contact.html',
                  {'title': 'Dashboard', 'data': 'Contacts Exported Successfully!'})
