from django.urls import path

from . import views


app_name = "challenge"

urlpatterns = [
    path("", views.home, name="home"),
    path("fibonacci/", views.fibonacci_view, name="fibonacci"),
    path("login/", views.login_view, name="login"),
    path("javascript/", views.javascript_view, name="javascript"),
    path("php/", views.cli_exercise_view, name="php"),
    # Preserve the original static site URLs for direct comparisons and bookmarks.
    path("index.html", views.home, name="original_home"),
    path("PHP/index.html", views.cli_exercise_view, name="original_php"),
    path("JAVASCRIPT/index.html", views.javascript_view, name="original_javascript"),
    path("CSS/index.html", views.login_view, name="original_css"),
]
