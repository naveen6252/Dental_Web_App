# Generated by Django 3.0.2 on 2020-02-09 08:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient_registration', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='image',
            field=models.ImageField(default='default.jpg', upload_to='profile_pics'),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='contact',
            field=models.CharField(max_length=12, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+919999999'", regex='^\\+?1?\\d{9,12}$')]),
        ),
        migrations.AlterField(
            model_name='patient',
            name='mobile',
            field=models.CharField(max_length=12, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+919999999'", regex='^\\+?1?\\d{9,12}$')]),
        ),
    ]
