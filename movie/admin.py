from django.contrib import admin
from movie.models import *

# Register your models here.

admin.site.register(Genre)
admin.site.register(Language)
admin.site.register(Movie)
admin.site.register(Theater)
admin.site.register(Seat)
admin.site.register(Booking)
admin.site.register(Payment)