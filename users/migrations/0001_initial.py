# Generated by Django 4.2.21 on 2025-05-29 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Signup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('confirmpassword', models.CharField(max_length=255)),
                ('date', models.DateField()),
            ],
        ),
    ]
