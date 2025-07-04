# Generated by Django 4.2.21 on 2025-06-08 05:15

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_initial'),
        ('movie', '0010_seat'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.CharField(max_length=10)),
                ('booked_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movie.movie')),
                ('seats', models.ManyToManyField(to='movie.seat')),
                ('theater', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movie.theater')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.signup')),
            ],
        ),
    ]
