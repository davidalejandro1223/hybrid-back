# Generated by Django 3.2.6 on 2021-08-23 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0017_alter_branchofficeconfig_days_to_review_contagious'),
    ]

    operations = [
        migrations.AlterField(
            model_name='areaconfig',
            name='fase',
            field=models.CharField(choices=[('FASEI', 'Fase I'), ('FASEII', 'Fase II'), ('FASEIII', 'Fase III'), ('FASEIV', 'Fase IV'), ('Sin fase', 'Sin fase')], max_length=250),
        ),
    ]