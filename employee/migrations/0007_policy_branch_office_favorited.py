# Generated by Django 3.2.6 on 2021-08-23 18:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0016_alter_branchofficeconfig_maximun_request_days_contagious'),
        ('employee', '0006_auto_20210822_1734'),
    ]

    operations = [
        migrations.AddField(
            model_name='policy',
            name='branch_office_favorited',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='infrastructure.branchoffice'),
        ),
    ]