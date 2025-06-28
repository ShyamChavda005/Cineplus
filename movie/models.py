from django.db import models
from users.models import Signup
from django.utils import timezone

# Create your models here.

class Genre(models.Model) :
    name = models.CharField(max_length=50,unique=True)

    def __str__(self):
        return self.name
    
class Language(models.Model) :
    name = models.CharField(max_length=50,unique=True)

    def __str__(self):
        return self.name

class Movie(models.Model):
    name= models.CharField(max_length=255)
    description= models.TextField(blank=True,null=True) 
    poster = models.ImageField(upload_to="movies/")
    rate = models.DecimalField(max_digits=3,decimal_places=1)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    cast= models.TextField()
    release_date = models.DateField()

    def __str__(self):
        return self.name

class Theater(models.Model):
    name = models.CharField(max_length=255)
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE,related_name='theaters')
    datetime= models.DateTimeField()

    def __str__(self):
        return f'{self.name} = {self.movie.name}'

class Seat(models.Model):
    theater = models.ForeignKey(Theater,on_delete=models.CASCADE,related_name='seats')
    seat_number = models.CharField(max_length=20)
    is_booked=models.BooleanField(default=False)

    def __str__(self):
        return f'{self.seat_number} booked in {self.theater.name}'

class Booking(models.Model):
    user = models.ForeignKey(Signup, on_delete=models.CASCADE)
    seats = models.ManyToManyField(Seat)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    amount = models.CharField(max_length=10)
    booked_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username} booked {self.seats.count()} seat for {self.amount} at {self.theater.name}'

    