from django.shortcuts import render, get_object_or_404, redirect
from movie.models import *
from users.models import *
from django.contrib import messages

# Create your views here.

def movies(request) :
    movies = Movie.objects.all()
    return render(request,"movie/movies.html", {'movies' : movies})

def ticket(request,movieid) :
    if not request.session.get("user") :
        messages.error(request, "Signin Required for booking")
        return redirect("signin")

    movie = Movie.objects.get(id=movieid)
    theaters = Theater.objects.filter(movie=movie)

    theater_dict = {}

    for t in theaters:
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
        date = request.POST.get('date')
        time = request.POST.get('time')

        request.session['movie_id'] = movie_id
        request.session['tickets'] = tickets
        request.session['totalAmount'] = totalAmount
        request.session['theater_id'] = theater_id
        request.session['date'] = date
        request.session['time'] = time

        return redirect('seat')

    return render(request,"movie/ticket.html",{'movie':movie, 'theater_shows' : theater_shows})

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

def payment(request):
    if not request.session.get("user") :
        messages.error(request, "Signin Required for booking")
        return redirect("signin")
    
    selected_seats = request.session.get('selected_seats', [])
    total_amount = request.session.get('totalAmount')
    movie_id = request.session.get('movie_id')
    theater_id = request.session.get('theater_id')
    user = request.session.get('user')  # Assuming user login saved this

    movie = Movie.objects.get(id=movie_id)
    theater = Theater.objects.get(id=theater_id)
    user = Signup.objects.get(username=user)

    if request.method == 'POST':
        # 1. Create a booking instance
        booking = Booking.objects.create(
            user=user,
            movie=movie,
            theater=theater,
            amount=total_amount,
            booked_at=timezone.now()
        )

        # 2. Fetch Seat instances and add them
        for seat_num in selected_seats:
            seat = Seat.objects.get(theater=theater, seat_number=seat_num)
            booking.seats.add(seat)

        booking.save()

        messages.success(request, 'Payment successful! Your seats are booked.')

    context = {
        'selected_seats': selected_seats,
        'total_amount': total_amount,
        'movie': movie,
        'theater': theater,
    }

    return render(request, "movie/payment.html", context)
