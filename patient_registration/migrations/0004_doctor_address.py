# Generated by Django 3.0.2 on 2020-02-15 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient_registration', '0003_doctor_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='address',
            field=models.TextField(default='101 Gateway, Opp Shyamdham Mandir, Sarthana Jakat Naka, Surat'),
            preserve_default=False,
        ),
    ]
