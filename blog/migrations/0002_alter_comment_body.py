# Generated by Django 3.2.3 on 2021-06-17 19:03

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='body',
            field=models.TextField(validators=[django.core.validators.MinLengthValidator(15)]),
        ),
    ]
