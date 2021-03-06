from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.urls import reverse
from django.db.models import Sum
from PIL import Image


class Doctor(models.Model):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,12}$',
                                 message="Phone number must be entered in the format: '+919999999'")
    name = models.CharField(max_length=50)
    logo = models.ImageField(default='default_logo.jpg', upload_to='doctor_logo')
    address = models.TextField()
    contact = models.CharField(max_length=12, validators=[phone_regex])
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
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,12}$',
                                 message="Phone number must be entered in the format: '+919999999'")
    patient_id = models.IntegerField(unique=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics', blank=True)
    name = models.CharField(max_length=50)
    mobile1 = models.CharField(max_length=12, validators=[phone_regex])
    mobile2 = models.CharField(max_length=12, validators=[phone_regex], blank=True)
    sex = models.IntegerField(choices=gender_choices)
    address = models.TextField()
    birth_date = models.DateField()
    register_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.patient_id) + '-' + self.name

    def get_absolute_url(self):
        return reverse('patient-registration-view-patient', kwargs={'pk': self.id})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 240 or img.width > 240:
            output_size = (240, 240)
            img.thumbnail(output_size)
            img.save(self.image.path)

    @property
    def total_deposit(self):
        total_deposit = self.invoice_set.aggregate(Sum('deposit'))['deposit__sum']
        return total_deposit if total_deposit else 0.0

    @property
    def total_service(self):
        total_service = Service.objects.filter(invoice__patient=self).aggregate(Sum('amount'))['amount__sum']
        return total_service if total_service else 0.0

    @property
    def due_amount(self):
        return self.total_service - self.total_deposit

    @property
    def age(self):
        return timezone.now().date().year - self.birth_date.year


class Invoice(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    deposit = models.FloatField(default=0)
    invoice_date = models.DateTimeField(default=timezone.now)
    note = models.TextField(blank=True)

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        return reverse('patient-registration-view-invoice', kwargs={'pk': self.id})


class Treatment(models.Model):
    treatment = models.CharField(max_length=50)

    def __str__(self):
        return str(self.treatment)

    def get_absolute_url(self):
        return reverse('patient-registration-patients')


class Service(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE)
    tooth = models.CharField(blank=True, max_length=50)
    service_date = models.DateTimeField(default=timezone.now)
    laboratory_name = models.CharField(max_length=50, blank=True)
    amount = models.FloatField()
    description = models.TextField(blank=True)

    def __str__(self):
        return str(self.treatment)

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
        return reverse('patient-registration-view-appointment', kwargs={'doc_id': self.doctor.id})


class ExpenseType(models.Model):
    type = models.CharField(max_length=50)

    def __str__(self):
        return str(self.type)


class Expense(models.Model):
    type = models.ForeignKey(ExpenseType, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '{0} {1}'.format(self.type, self.date)

    def get_absolute_url(self):
        return reverse('patient-registration-view-expense')
