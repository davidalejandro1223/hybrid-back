# Generated by Django 3.2.6 on 2021-08-22 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0008_alter_areaconfig_fase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branchofficeconfig',
            name='maximun_request_days_contagious',
            field=models.IntegerField(default=14, verbose_name='dias de cuarentena/riesgo establecidos por sucursal'),
        ),
    ]