# Generated by Django 3.2.6 on 2021-08-22 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0007_merge_0005_auto_20210822_1633_0006_auto_20210822_1746'),
    ]

    operations = [
        migrations.AlterField(
            model_name='areaconfig',
            name='fase',
            field=models.CharField(choices=[('FASEI', 'Fase I'), ('FASEII', 'Fase II'), ('FASEIII', 'Fase III'), ('FASEIV', 'Fase IV'), ('FASEV', 'Fase V'), ('Sin fase', 'Sin fase')], max_length=250),
        ),
    ]
