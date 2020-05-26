from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Sum
from .models import Patient, Doctor, Appointment, Service, Invoice, Treatment, Expense, ExpenseType
from datetime import timedelta
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from googleapiclient.discovery import build
from .social_google_credentials import Credentials
from social_django.utils import load_strategy
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
from threading import Thread
import time

TOTAL_CONTACTS = 0
SYNCED_CONTACTS = 0
CONTACT_THREAD = None


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
    mtd_sales = mtd_sales if mtd_sales else 0
    last_month_sale = Invoice.objects.filter(
        invoice_date__gte=last_month_first_date, invoice_date__lte=last_month_last_date).aggregate(
        Sum('deposit'))['deposit__sum']
    last_month_sale = last_month_sale if last_month_sale else 0
    mom_growth = round(((mtd_sales - last_month_sale) / last_month_sale) * 100, 1) if last_month_sale > 0 else 100

    mtd_expenses = Expense.objects.filter(
        date__gte=month_first_date, date__lte=today).aggregate(Sum('amount'))['amount__sum']
    mtd_expenses = mtd_expenses if mtd_expenses else 0
    last_month_expenses = Expense.objects.filter(date__gte=last_month_first_date,
                                                 date__lte=last_month_last_date).aggregate(Sum('amount'))['amount__sum']
    last_month_expenses = last_month_expenses if last_month_expenses else 0
    expense_growth = round(((mtd_expenses - last_month_expenses) / last_month_expenses) * 100,
                           1) if last_month_expenses > 0 else 100

    total_appointments = Appointment.objects.count()
    completed_appointments = Appointment.objects.filter(date__lte=timezone.now()).count()
    appointment_percent = int((completed_appointments / total_appointments) * 100) if total_appointments else 100

    revenue = Service.objects.aggregate(Sum('amount'))['amount__sum']
    revenue = revenue if revenue else 0
    deposit_amount = Invoice.objects.aggregate(Sum('deposit'))['deposit__sum']
    due = revenue - deposit_amount
    total_invoices = Invoice.objects.count()

    mom_chart = {
        'bindto': '#mom-chart',
        'data': {
            'columns': [
                ['Service Amount'],
                ['Deposit Amount']
            ],
            'type': 'line',
            'groups': [
                ['Service Amount', 'Deposit Amount']
            ],
            'colors': {
                'Service Amount': "#3866a6",
                'Deposit Amount': "#b93d30"
            },
        },
        'axis': {
            'x': {
                'type': 'category',
                'categories': []
            },
        },
        'legend': {
            'show': True,
        },
        'padding': {
            'bottom': 0,
            'top': 0,
        },
        'grid': {
            'x': {
                'show': True
            },
            'y': {
                'show': True
            }
        },
    }
    expense_trend = {
        'bindto': '#expense-trend',
        'data': {
            'columns': [
                ['Expense Amount']
            ],
            'type': 'line',
            'colors': {
                'Expense Amount': "#3866a6"
            },
        },
        'axis': {
            'x': {
                'type': 'category',
                'categories': []
            },
        },
        'bar': {
            'width': 60,
        },
        'legend': {
            'show': True,
        },
        'padding': {
            'bottom': 0,
            'top': 0,
        },
        'grid': {
            'x': {
                'show': True
            },
            'y': {
                'show': True
            }
        },
    }
    total_last_months = 11
    while total_last_months >= 0:
        curr_date = timezone.now() - relativedelta(months=total_last_months)
        curr_month_service = Service.objects.filter(service_date__month=curr_date.month,
                                                    service_date__year=curr_date.year).aggregate(
            Sum('amount'))['amount__sum']
        curr_month_service = curr_month_service if curr_month_service else 0
        curr_month_deposit = \
            Invoice.objects.filter(invoice_date__month=curr_date.month, invoice_date__year=curr_date.year).aggregate(
                Sum('deposit'))['deposit__sum']
        curr_month_deposit = curr_month_deposit if curr_month_deposit else 0
        curr_month_expense = Expense.objects.filter(date__month=curr_date.month, date__year=curr_date.year).aggregate(
            Sum('amount'))['amount__sum']

        month_year = curr_date.strftime('%b-%Y')
        mom_chart['data']['columns'][0].append(curr_month_service)
        mom_chart['data']['columns'][1].append(curr_month_deposit)
        mom_chart['axis']['x']['categories'].append(month_year)

        expense_trend['data']['columns'][0].append(curr_month_expense)
        expense_trend['axis']['x']['categories'].append(curr_date.strftime('%b-%y'))

        total_last_months -= 1

    treatment_chart = {
        'bindto': '#treatment-chart',
        'data': {
            'columns': [
                ['revenue'],
                ['due']
            ],
            'types': {
                'due': "line",
                'revenue': 'bar'
            },
            'groups': [
                ['revenue']
            ],
            'colors': {
                'revenue': '#7DCBD2',
                'due': '#140D5F',
            },
        },
        'axis': {
            'x': {
                'type': 'category',
                'categories': []
            },
        },
        'bar': {
            'width': '50%',
        },
        'legend': {
            'show': True,
        },
        'padding': {
            'bottom': 0,
            'top': 0
        },
    }
    for treatment in Treatment.objects.all():
        treatment_chart['axis']['x']['categories'].append(treatment.treatment)
        treatment_revenue = Service.objects.filter(treatment=treatment).aggregate(Sum('amount'))['amount__sum']
        treatment_revenue = treatment_revenue if treatment_revenue else 0
        treatment_deposit = Invoice.objects.filter(service__treatment=treatment).aggregate(Sum('deposit'))[
            'deposit__sum']
        treatment_deposit = treatment_deposit if treatment_deposit else 0
        treatment_due = treatment_revenue - treatment_deposit
        treatment_chart['data']['columns'][0].append(treatment_revenue)
        treatment_chart['data']['columns'][1].append(treatment_due)

    appointment_by_doctor = [[doctor.name, doctor.appointment_set.count()] for doctor in Doctor.objects.all()]

    expense_amount = [[expense.type, expense.expense_set.aggregate(Sum('amount'))['amount__sum']] for expense in
                      ExpenseType.objects.all()]

    context = {
        'title': 'Dashboard',
        'total_patients': total_patients,
        'mtd_patients': curr_month_patients,
        'mtd_sales': mtd_sales,
        'mom_growth': mom_growth,
        'mtd_expenses': mtd_expenses,
        'expense_growth': expense_growth,
        'total_appointments': total_appointments,
        'completed_appointments': appointment_percent,
        'revenue': revenue,
        'due': due,
        'invoices': total_invoices,
        'mom_chart': json.dumps(mom_chart),
        'treatment_chart': json.dumps(treatment_chart),
        'appointment_by_doctor': json.dumps(appointment_by_doctor),
        'expense_amount': json.dumps(expense_amount),
        'expense_trend': json.dumps(expense_trend)
    }

    return render(request, 'patient_registration/dashboard.html', context)


class PatientListView(LoginRequiredMixin, ListView):
    model = Patient

    def get_context_data(self, **kwargs):
        context = super(PatientListView, self).get_context_data(**kwargs)

        context['title'] = 'Patient'
        return context


class PatientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Patient

    def get_success_url(self):
        return reverse('patient-registration-patients')

    def get_context_data(self, **kwargs):
        context = super(PatientDeleteView, self).get_context_data(**kwargs)
        context['title'] = 'Patient Delete'
        return context

    def test_func(self):
        return self.request.user.is_superuser


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
    fields = ['name', 'image', 'mobile1', 'mobile2', 'sex', 'birth_date', 'address']

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
    fields = ['patient_id', 'name', 'image', 'mobile1', 'mobile2', 'sex', 'birth_date', 'address']

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


class DoctorUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Doctor
    fields = ['name', 'contact', 'designation', 'logo', 'address']

    def get_context_data(self, **kwargs):
        context = super(DoctorUpdateView, self).get_context_data(**kwargs)
        context['title'] = 'Doctor'
        return context

    def test_func(self):
        return self.request.user.is_superuser


class DoctorListView(LoginRequiredMixin, ListView):
    model = Doctor

    def get_context_data(self, **kwargs):
        context = super(DoctorListView, self).get_context_data(**kwargs)
        context['title'] = 'Doctor'
        return context


class DoctorDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Doctor

    def get_success_url(self):
        return reverse('patient-registration-doctors')

    def get_context_data(self, **kwargs):
        context = super(DoctorDeleteView, self).get_context_data(**kwargs)
        context['title'] = 'Doctor Delete'
        return context

    def test_func(self):
        return self.request.user.is_superuser


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


class AppointmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Appointment

    def get_success_url(self):
        return reverse('patient-registration-view-appointment', kwargs={'doc_id': self.get_object().doctor.id})

    def get_context_data(self, **kwargs):
        context = super(AppointmentDeleteView, self).get_context_data(**kwargs)
        context['title'] = 'Appointment - Delete'
        return context

    def test_func(self):
        return self.request.user.is_superuser


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


@login_required
def export_data(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="PatientData' + timezone.now().astimezone().strftime(
        '%Y%m%d_%H%M%S') + '.csv"'
    writer = csv.writer(response)

    writer.writerow(['Patient_ID', 'Patient Name', 'Mobile1', 'Mobile2', 'Age', 'Sex', 'Address', 'Registered Date',
                     'Doctor Name', 'Invoice ID', 'Invoice Date', 'Deposit', 'Invoice Note', 'Service ID', 'Treatment',
                     'Tooth', 'Treatment Date', 'Laboratory', 'Treatment Amount', 'Treatment Description'])

    services = Service.objects.all()
    for service in services:
        invoice = service.invoice
        patient = invoice.patient
        doctor = invoice.doctor
        row = [patient.patient_id, patient.name, patient.mobile1, patient.mobile2, patient.age, patient.sex,
               patient.address, patient.register_date, doctor.name, invoice.id, invoice.invoice_date, invoice.deposit,
               invoice.note, service.id, service.treatment.treatment, service.tooth, service.service_date,
               service.laboratory_name, service.amount, service.description]
        writer.writerow(row)

    invoices = Invoice.objects.filter(service__isnull=True)
    for invoice in invoices:
        patient = invoice.patient
        doctor = invoice.doctor
        row = [patient.patient_id, patient.name, patient.mobile1, patient.mobile2, patient.age, patient.sex,
               patient.address, patient.register_date, doctor.name, invoice.id, invoice.invoice_date, invoice.deposit,
               invoice.note, '', '', '', '', '', '', '']
        writer.writerow(row)
    return response


@login_required
def daily_report(request):
    response = HttpResponse(content_type='text/csv')
    response[
        'Content-Disposition'] = 'attachment; filename="Harbor_Daily_Report_' + timezone.now().astimezone().strftime(
        '%Y%m%d_%H%M%S') + '.csv"'
    writer = csv.writer(response)

    writer.writerow(['Patient_ID', 'Patient Name', 'Mobile1', 'Mobile2', 'Age', 'Sex', 'Address', 'Registered Date',
                     'Doctor Name', 'Invoice ID', 'Invoice Date', 'Deposit', 'Invoice Note', 'Service ID', 'Treatment',
                     'Tooth', 'Treatment Date', 'Laboratory', 'Treatment Amount', 'Treatment Description'])

    today_services = Service.objects.filter(service_date__gte=timezone.now().date())
    for service in today_services:
        invoice = service.invoice
        patient = invoice.patient
        doctor = invoice.doctor
        row = [patient.patient_id, patient.name, patient.mobile1, patient.mobile2, patient.age, patient.sex,
               patient.address, patient.register_date, doctor.name, invoice.id, invoice.invoice_date, invoice.deposit,
               invoice.note, service.id, service.treatment.treatment, service.tooth, service.service_date,
               service.laboratory_name, service.amount, service.description]
        writer.writerow(row)

    today_invoices = Invoice.objects.filter(service__isnull=True, invoice_date__gte=timezone.now().date())
    for invoice in today_invoices:
        patient = invoice.patient
        doctor = invoice.doctor
        row = [patient.patient_id, patient.name, patient.mobile1, patient.mobile2, patient.age, patient.sex,
               patient.address, patient.register_date, doctor.name, invoice.id, invoice.invoice_date, invoice.deposit,
               invoice.note, '', '', '', '', '', '', '']
        writer.writerow(row)

    today_registered_patients = Patient.objects.filter(register_date=timezone.now().date())
    for patient in today_registered_patients:
        row = [patient.patient_id, patient.name, patient.mobile1, patient.mobile2, patient.age, patient.sex,
               patient.address, patient.register_date, '', '', '', '', '', '', '', '', '', '', '', '']
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


def export_contacts_async(service):
    people = service.people().connections().list(resourceName='people/me', personFields='names').execute()

    existing_patient_contact = []

    if people:
        next_page_token = people.get("nextPageToken")
        connections_list = people.get("connections")

        while next_page_token:
            people = service.people().connections().list(resourceName='people/me', pageToken=next_page_token,
                                                         personFields='names').execute()
            if people.get("connections"):
                connections_list += people.get("connections")
            next_page_token = people.get("nextPageToken")

        for val in connections_list:
            if val.get('names'):
                for name in val.get('names'):
                    if name.get("honorificPrefix"):
                        existing_patient_contact.append(name.get("honorificPrefix"))

    global SYNCED_CONTACTS
    SYNCED_CONTACTS = 0
    for patient in Patient.objects.all():
        if str(patient.patient_id) not in existing_patient_contact:
            service.people().createContact(
                body={
                    "names": [
                        {"displayName": patient.name, "givenName": patient.name,
                         "honorificPrefix": str(patient.patient_id)}],
                    "phoneNumbers": [
                        {
                            'value': patient.mobile1
                        }
                    ],
                    'organizations': [{
                        'name': 'Harbor-dental',
                        'title': 'Patient'
                    }]
                }
            ).execute()
            time.sleep(0.2)
        SYNCED_CONTACTS = SYNCED_CONTACTS + 1
    return


@login_required
def export_contacts(request):
    if not request.user.social_auth.filter(provider='google-oauth2'):
        return redirect('social:begin', 'google-oauth2')
    social = request.user.social_auth.get(provider='google-oauth2')

    if social.access_token_expired():
        social.refresh_token(load_strategy())

    service = build('people', 'v1', credentials=Credentials(social))
    global CONTACT_THREAD
    global SYNCED_CONTACTS
    if not CONTACT_THREAD:
        CONTACT_THREAD = Thread(target=export_contacts_async, args=(service,), name='ContactThread')
        CONTACT_THREAD.start()

    if not CONTACT_THREAD.is_alive():
        CONTACT_THREAD = Thread(target=export_contacts_async, args=(service,), name='ContactThread')
        CONTACT_THREAD.start()

    global TOTAL_CONTACTS
    TOTAL_CONTACTS = Patient.objects.count()

    return render(request, 'patient_registration/export-contact.html',
                  {'title': 'Dashboard',
                   'data': '{0} out of {1} Contacts Exported Successfully!'.format(SYNCED_CONTACTS, TOTAL_CONTACTS)})
