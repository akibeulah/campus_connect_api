# Generated by Django 3.2.5 on 2022-05-11 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0014_poshandovers'),
    ]

    operations = [
        migrations.AddField(
            model_name='poshandovers',
            name='request_desc',
            field=models.TextField(null=True),
        ),
    ]
