# Generated by Django 3.2.6 on 2021-08-22 03:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0002_policy'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workgroup',
            name='employee',
        ),
        migrations.RemoveField(
            model_name='workgroup',
            name='work_position',
        ),
        migrations.DeleteModel(
            name='BaseWorkGroup',
        ),
        migrations.DeleteModel(
            name='WorkGroup',
        ),
    ]