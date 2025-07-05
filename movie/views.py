from django.shortcuts import render, get_object_or_404, redirect
from movie.models import *
from users.models import *
from django.contrib import messages
from datetime import *
from django.utils.timezone import localtime  
import requests
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def movies(request) :
    genre = request.GET.get("genre")
    language = request.GET.get("language")

    movies = Movie.objects.all()
    if genre :
        movies = Movie.objects.filter(genre__name=genre)
    if language :
        movies = Movie.objects.filter(language__name=language)

    genres = Genre.objects.all()
    languages = Language.objects.all()

    context = {
        'movies' : movies,
        'genres' : genres,
        'languages' : languages,
        'select_genre' : genre,
        'select_language' : language,
    }

    return render(request,"movie/movies.html", context)

def ticket(request, movieid):
    if not request.session.get("user"):
        messages.error(request, "Signin Required for booking")
        return redirect("signin")

    movie = Movie.objects.get(id=movieid)
    theaters = Theater.objects.filter(movie=movie)

    today = date.today()
    theater_dict = {}

    for t in theaters:
        if today == localtime(t.datetime).date():
            if t.name not in theater_dict:
                theater_dict[t.name] = {'id': t.id, 'datetimes': []}
            theater_dict[t.name]['datetimes'].append(t.datetime)

    theater_shows = [
        {'id': data['id'], 'name': name, 'times': data['datetimes']}
        for name, data in theater_dict.items()
    ]

    if request.method == "POST":
        movie_id = request.POST.get('movie_id')
        tickets = request.POST.get('tickets')
        totalAmount = request.POST.get('totalAmount')
        theater_id = request.POST.get('theater_id')
        selected_date  = request.POST.get('date')
        time = request.POST.get('time')

        request.session['movie_id'] = movie_id
        request.session['tickets'] = tickets
        request.session['totalAmount'] = totalAmount
        request.session['theater_id'] = theater_id
        request.session['date'] = selected_date 
        request.session['time'] = time

        return redirect('seat')

    return render(request, "movie/ticket.html", {'movie': movie, 'theater_shows': theater_shows})


def seat(request):
    if not request.session.get("user") :
        messages.error(request, "Signin Required for booking")
        return redirect("signin")
    
    ticket_count = request.session.get('tickets')
    totalAmount = request.session.get('totalAmount')
    theater_id = request.session.get('theater_id')

    if not ticket_count or not theater_id:
        return redirect('ticket')

    theater = Theater.objects.get(id=theater_id)
    booked_seats = Seat.objects.filter(theater=theater, is_booked=True).values_list('seat_number', flat=True)

    if request.method == 'POST':
        selected_seats = request.POST.get('selected_seats', '').split(',')

        if len(selected_seats) != int(ticket_count):
            messages.error(request, "Please select the correct number of seats.")
            return redirect('seat')

        for seat_number in selected_seats:
            if not Seat.objects.filter(theater=theater, seat_number=seat_number, is_booked=True).exists():
                Seat.objects.create(
                    theater=theater,
                    seat_number=seat_number,
                    is_booked=True
                )
            else:
                messages.error(request, f"Seat {seat_number} is already booked. Please refresh and select again.")
                return redirect('seat')

        request.session['selected_seats'] = selected_seats
        return redirect('payment')  # change to your actual payment route name

    context = {
        'ticket_count': int(ticket_count),
        'totalAmount': totalAmount,
        'booked_seats': list(booked_seats),
    }

    return render(request, "movie/seat.html", context)


@csrf_exempt
def payment(request):
    if not request.session.get("user"):
        messages.error(request, "Signin Required for booking")
        return redirect("signin")
    
    selected_seats = request.session.get('selected_seats', [])
    total_amount = request.session.get('totalAmount')
    amount_str = str(total_amount).replace("₹", "").replace(",", "").strip()
    movie_id = request.session.get('movie_id')
    theater_id = request.session.get('theater_id')
    username = request.session.get('user')

    movie = Movie.objects.get(id=movie_id)
    theater = Theater.objects.get(id=theater_id)
    user = Signup.objects.get(username=username)

    # Generate unique order ID
    order_id = f"ORDER_{user.id}_{int(datetime.now().timestamp())}"
    request.session['cashfree_order_id'] = order_id

    if request.method == 'POST':
        # Call Cashfree to create order
        headers = {
            "x-client-id": settings.CASHFREE_APP_ID,
            "x-client-secret": settings.CASHFREE_SECRET_KEY,
            "x-api-version": "2022-09-01",
            "Content-Type": "application/json",
        }

        data = {
            "link_id": f"LINK_{user.id}_{int(datetime.now().timestamp())}",
            "link_amount": float(amount_str),
            "link_currency": "INR",
            "customer_details": {
                "customer_id": str(user.id),
                "customer_email": user.email,
                "customer_name": user.name,
                "customer_phone": user.phone
            },
            "link_notify": {
                "send_sms": True,
                "send_email": True
            },
            "link_purpose": "CinePlus Ticket Booking",
            "link_meta": {
                "return_url": f"http://127.0.0.1:8000/payment/callback/?order_id={order_id}"
            }
        }

        response = requests.post("https://sandbox.cashfree.com/pg/links", headers=headers, json=data)


        result = response.json()
        payment_link = result.get("link_url")

        if payment_link:
            return redirect(payment_link)
        else:
            messages.error(request, "Could not generate payment link.")


    context = {
        'selected_seats': selected_seats,
        'total_amount': total_amount,
        'movie': movie,
        'theater': theater,
    }

    return render(request, "movie/payment.html", context)


@csrf_exempt
def payment_callback(request):
    order_id = request.GET.get("order_id")
    session_order_id = request.session.get("cashfree_order_id")

    if order_id != session_order_id:
        messages.error(request, "Invalid payment verification.")
        # return redirect("movies")

    # Finalize booking
    selected_seats = request.session.get('selected_seats', [])
    total_amount = request.session.get('totalAmount')
    movie_id = request.session.get('movie_id')
    theater_id = request.session.get('theater_id')
    username = request.session.get('user')

    movie = Movie.objects.get(id=movie_id)
    theater = Theater.objects.get(id=theater_id)
    user = Signup.objects.get(username=username)

    booking = Booking.objects.create(
        user=user,
        movie=movie,
        theater=theater,
        amount=total_amount,
        booked_at=timezone.now()
    )

    for seat_num in selected_seats:
        seat = Seat.objects.get(theater=theater, seat_number=seat_num)
        seat.is_booked = True
        seat.save()
        booking.seats.add(seat)

    booking.save()

    # Clean up session
    for key in ['selected_seats', 'totalAmount', 'movie_id', 'theater_id', 'date', 'time', 'cashfree_order_id']:
        request.session.pop(key, None)

    return render(request, "movie/payment_success.html", {"booking": booking})