from django.urls import path

from . import views


app_name = "challenge"

urlpatterns = [
    path("", views.home, name="home"),
    path("fibonacci/", views.fibonacci_view, name="fibonacci"),
    path("login/", views.login_view, name="login"),
]
