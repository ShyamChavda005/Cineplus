from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from movie import views 

urlpatterns = [
  path('movies/',views.movies,name="movies"),
  path('ticket/<int:movieid>',views.ticket,name="ticket"),
  path('seat-selection/',views.seat,name="seat"),
  path('payment/',views.payment,name="payment"),
]


# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)