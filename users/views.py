import uuid
from django.core.mail import send_mail
from django.conf import settings
from users.models import Signup
from movie.models import *
from django.shortcuts import render, redirect
from django.contrib import messages
import random 

# Create your views here.

def signin(request) :
    if request.method == "POST" :
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = Signup.objects.get(username=username, password=password)
            request.session['user'] = user.username
            messages.success(request, "Login successful!")
            return redirect("index")
        
        except Signup.DoesNotExist:
            messages.error(request, "Invalid username or password")

    return render(request,"users/signin.html")


def signup(request) :
    if request.method == "POST" :
        name = request.POST.get('name')
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirmpassword = request.POST.get("confirmpassword")

        if not name or not email or not phone or not username or not password or not confirmpassword:
            messages.error(request, 'All fields are required.')
            return redirect('signup')  

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return redirect('signup')

        if password != confirmpassword :
            messages.error(request,"Password not match")
            return render(request,"users/signup.html")
        
        if Signup.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('signup')

        if Signup.objects.filter(username=username).exists() == True :
            messages.error(request,"Username already Exists")
            return render(request,"users/signup.html")
        
        try :
            sigup = Signup(name=name,email=email,phone=phone,username=username,password=password,confirmpassword=confirmpassword)
            sigup.save()
            messages.success(request, "Account Created! Login With register Username and password")
            return redirect("signin")

        except :
            messages.error(request,"Invalid Creditials")

    return render(request,"users/signup.html")


def profile(request):
    username = request.session.get('user')

    if not username :
        return redirect('signin')
    
    user = Signup.objects.get(username=username)

    if request.method == "POST":
        new_name = request.POST.get('name')
        new_email = request.POST.get('email')
        new_phone = request.POST.get('phone')
        new_username = request.POST.get('username')

        update = False

        if new_username != user.username:
            if Signup.objects.filter(username=new_username).exclude(id=user.id).exists():
                messages.error(request, "Username already exists.")
                return render(request, "users/profile.html", {'user': user})
            else:
                user.username = new_username
                request.session['user'] = new_username 
                update = True

        if new_name != user.name:
            user.name = new_name
            update = True

        if new_email != user.email:
            user.email = new_email
            update = True

        if new_phone != user.phone:
            user.phone = new_phone
            update = True

        if update:
            user.save()
            messages.success(request, "Profile updated successfully.")
        else:
            messages.info(request, "No changes detected.")

        return redirect('profile')
    
    return render(request,"users/profile.html",{'user': user})


def forget_password(request) :
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = Signup.objects.get(email=email)
            token = str(uuid.uuid4())

            request.session['reset_token'] = token
            request.session['reset_email'] = email

            reset_link = f"http://127.0.0.1:8000/reset-password/{token}/"

            send_mail(
                "Password Reset Request - Cineplus",
                f"Hi {user.name},\n\nClick the link below to reset your password:\n{reset_link}\n\nIf you didn't request this, ignore this email.",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            messages.success(request, "Reset link has been sent to your email.")
            return redirect("forget_password")

        except Signup.DoesNotExist:
            messages.error(request, "This email is not registered.")

    return render(request, "users/forget-password.html")


def reset_password(request, token):
    saved_token = request.session.get('reset_token')
    saved_email = request.session.get('reset_email')

    if token != saved_token:
        messages.error(request, "Invalid or expired reset link.")
        return redirect("signin")

    if request.method == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirmpassword")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "users/reset-password.html")

        try:
            user = Signup.objects.get(email=saved_email)
            user.password = new_password 
            user.confirmpassword = new_password
            user.save()
            messages.success(request, "Password updated successfully.")
            return redirect("signin")

        except Signup.DoesNotExist:
            messages.error(request, "User not found.")

    return render(request, "users/reset-password.html")


def update_password(request) :
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = Signup.objects.get(email=email)
            otp = random.randint(000000,999999)

            request.session['otp'] = otp
            request.session['email'] = email

            send_mail(
                "Password Update Request - Cineplus",
                f"Hi {user.name},\n\nOtp for update password is :\n{otp}\n\nIf you didn't request this, ignore this email.",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            messages.success(request, "Otp has been sent to your email.")
            return redirect("otp_verification")

        except Signup.DoesNotExist:
            messages.error(request, "This email is not registered.")

    return render(request, "users/update-password.html")


def otp_verification(request):
    otp = str(request.session.get("otp"))
    email = request.session.get("email")

    if request.method == "POST":
        o1 = request.POST.get("o1")
        o2 = request.POST.get("o2")
        o3 = request.POST.get("o3")
        o4 = request.POST.get("o4")
        o5 = request.POST.get("o5")
        o6 = request.POST.get("o6")

        input_otp = "".join([str(o1), str(o2), str(o3), str(o4), str(o5), str(o6)])

        if otp == input_otp :
            messages.success(request, "Otp verified successfully.")
            return redirect("change_password")
        
        else :
            messages.error(request, "Invalid Otp.")
            return redirect("otp_verification")


    return render(request,"users/otp_verification.html")


def change_password(request) :
    email = request.session.get('email')

    if request.method == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirmpassword")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "users/change-password.html")

        try:
            user = Signup.objects.get(email=email)
            user.password = new_password  
            user.confirmpassword = new_password
            user.save()
            messages.success(request, "Password updated successfully.")
            request.session.flush()
            return redirect("signin")

        except Signup.DoesNotExist:
            messages.error(request, "User not found.")

    return render(request,"users/change-password.html")


def logout(request) :
    request.session.flush()
    return redirect("signin")


def history(request):
    username = request.session.get('user')
    if not username :
        messages.error(request, "Signin Required for booking")
        return redirect("signin")
    
    user = Signup.objects.get(username=username)
    bookings = Booking.objects.filter(user=user).order_by('-booked_at')
    payments = Payment.objects.filter(user=user).order_by('-created_at')

    context = {
        'bookings': bookings,
        "payments" : payments
    }
    return render(request, 'users/history.html', context)