# Generated by Django 3.1.6 on 2021-02-20 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ZakharovMachineLearn', '0003_estimation'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='estimation_amount',
            field=models.IntegerField(default=0),
        ),
    ]