from django.contrib import admin
from django.urls import path, include
# from home import views
from users import views as users_views

urlpatterns = [
  path("signin/",users_views.signin,name="signin"),
  path("signup/",users_views.signup,name="signup"),
  path("profile/",users_views.profile,name="profile"),
  path("logout/",users_views.logout,name="logout"),
  path("forget-password/",users_views.forget_password,name="forget_password"),
  path("reset-password/<str:token>/", users_views.reset_password, name="reset_password"),
  path("update-password/", users_views.update_password, name="update_password"),
  path("otp-verification/", users_views.otp_verification, name="otp_verification"),
  path("change-password/", users_views.change_password, name="change_password"),
  path('history/',users_views.history,name="history"),
]
