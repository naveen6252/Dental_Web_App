from django.urls import path
from . import views
from .views import PatientCreateView, AppointmentCreateView, PatientListView, PatientDeleteView, \
    ServiceCreateView, DoctorCreateView, DoctorListView, DoctorDeleteView, DoctorUpdateView, InvoiceCreateView, \
    AppointmentUpdateView, InvoiceDetailView

urlpatterns = [
    path('', views.home, name='patient-registration-home'),
    path('patient/new/', PatientCreateView.as_view(), name='patient-registration-add-patient'),
    path('doctor/new', DoctorCreateView.as_view(), name='patient-registration-add-doctor'),
    path('patient/', PatientListView.as_view(), name='patient-registration-patients'),
    path('doctor/', DoctorListView.as_view(), name='patient-registration-doctors'),
    path('patient/<int:pk>/delete/', PatientDeleteView.as_view(), name='patient-registration-delete-patient'),
    path('doctor/<int:pk>/delete/', DoctorDeleteView.as_view(), name='patient-registration-delete-doctor'),
    path('doctor/<int:pk>/update/', DoctorUpdateView.as_view(), name='patient-registration-update-doctor'),
    path('invoice/<int:p_id>/new/', InvoiceCreateView.as_view(), name='patient-registration-add-invoice'),
    path('invoice/<int:pk>/', InvoiceDetailView.as_view(), name='patient-registration-view-invoice'),
    path('service/<int:p_id>/new/', views.add_invoice_service, name='patient-registration-add-invoice-service'),
    path('service/more/<int:inv_id>/new/', ServiceCreateView.as_view(), name='patient-registration-add-more-service'),
    path('appointment/patient/<int:p_id>/new/', AppointmentCreateView.as_view(),
         name='patient-registration-add-appointment'),
    path('appointment/<int:pk>/update/', AppointmentUpdateView.as_view(),
         name='patient-registration-update-appointment'),
    path('appointment/doctor/<int:doc_id>/', views.appointments, name='patient-registration-view-appointment'),

]
