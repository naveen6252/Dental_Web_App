from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='patient-registration-home'),
]