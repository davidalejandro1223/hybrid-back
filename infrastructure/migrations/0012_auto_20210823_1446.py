# Generated by Django 3.2.6 on 2021-08-23 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0011_auto_20210823_1445'),
    ]

    operations = [
        migrations.AddField(
            model_name='reserva',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='fecha y hora fin jornada'),
        ),
        migrations.AddField(
            model_name='reserva',
            name='start_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='fecha y hora inicio jornada'),
        ),
    ]
