# Generated by Django 3.2.6 on 2021-08-22 03:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_user_cellphone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='mobility_permit',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='Pase de movilidad'),
        ),
    ]
