from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Sum
from .models import Patient, Doctor, Appointment, Service, Invoice, Treatment
from datetime import datetime, timedelta
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
def home(request):
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
        context['invoices'] = Invoice.objects.filter(patient=patient).order_by('-invoice_date')
        context['amt_total'] = context['services'].aggregate(Sum('amount'))['amount__sum']
        context['deposit_total'] = context['invoices'].aggregate(Sum('deposit'))['deposit__sum']
        context['due_amt'] = context['deposit_total'] - context['amt_total']

        context['title'] = 'Patient'
        return context


class PatientCreateView(LoginRequiredMixin, CreateView):
    model = Patient
    fields = ['name', 'mobile', 'age', 'sex', 'address']

    def form_valid(self, form):
        number = Patient.objects.filter(register_date__date=datetime.today().date()).count() + 1
        number = '0' + str(number) if number < 10 else str(number)
        p_id = datetime.today().strftime('%Y%m%d') + number
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
        context['title'] = 'Treatment'
        return context


class PatientUpdateView(LoginRequiredMixin, UpdateView):
    model = Patient
    fields = ['patient_id', 'name', 'mobile', 'age', 'sex', 'address']

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
    fields = ['name', 'contact', 'designation']

    def get_context_data(self, **kwargs):
        context = super(DoctorCreateView, self).get_context_data(**kwargs)
        context['title'] = 'Doctor'
        return context


class DoctorUpdateView(LoginRequiredMixin, UpdateView):
    model = Doctor
    fields = ['name', 'contact', 'designation']

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
        context['title'] = 'Patient Registration'
        return context


class AppointmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Appointment
    fields = ['doctor', 'patient', 'date', 'note']

    def get_context_data(self, **kwargs):
        context = super(AppointmentUpdateView, self).get_context_data(**kwargs)
        context['title'] = 'Patient Registration'
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

    next_appointments = current_appointments.filter(date__gte=datetime.now()).order_by('date')
    context = {'appointments_json': all_appointments, 'title': 'Doctor', 'doctor': doctor, 'form': appointment_form,
               'next_appointments': next_appointments, 'appointments': current_appointments}
    return render(request, 'patient_registration/appointments.html', context)


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice

    def get_context_data(self, **kwargs):
        context = super(InvoiceDetailView, self).get_context_data(**kwargs)
        context['title'] = 'Invoice'
        context['sub_total'] = self.get_object().service_set.aggregate(Sum('amount'))['amount__sum']
        context['balance'] = self.get_object().deposit - context['sub_total']
        return context


class InvoiceSlipView(LoginRequiredMixin, DetailView):
    model = Patient
    template_name = 'patient_registration/invoice_slip.html'

    def get_context_data(self, **kwargs):
        context = super(InvoiceSlipView, self).get_context_data(**kwargs)
        patient = self.get_object()
        context['title'] = 'Invoice'
        context['amount_total'] = Service.objects.filter(
            invoice__patient=patient).aggregate(Sum('amount'))['amount__sum']
        context['deposit_total'] = Invoice.objects.filter(patient=patient).aggregate(Sum('deposit'))[
            'deposit__sum']
        context['balance'] = context['deposit_total'] - context['amount_total']
        return context


@login_required
def export_data(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="PatientData' + datetime.now().astimezone().strftime(
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
