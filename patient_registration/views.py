from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.urls import reverse
from django.db.models import Sum
from .models import Patient, Doctor, Appointment, Service, Invoice
from datetime import datetime, timedelta
from .forms import InvoiceCreateForm, ServiceCreateForm, AppointmentCreateForm
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
    ordering = ['-register_date']

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


@login_required
def appointments(request, doc_id):
    appointments_array = []
    for appointment in Appointment.objects.filter(doctor__id=doc_id):
        start = appointment.date
        end = start + timedelta(minutes=30)
        appointments_array.append(
            {'title': str(appointment.patient.patient_id) + '-' + appointment.patient.name,
             'start': start.astimezone().strftime('%Y-%m-%dT%H:%M:%S'),
             'end': end.astimezone().strftime('%Y-%m-%dT%H:%M:%S'),
             'note': appointment.note, 'appointment_id': appointment.id, 'allDay': False}
        )

    all_appointments = json.dumps(appointments_array)
    doctor = Doctor.objects.get(id=doc_id)
    context = {'appointments': all_appointments, 'title': 'Doctor', 'doctor': doctor}
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
