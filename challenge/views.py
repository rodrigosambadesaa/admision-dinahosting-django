from django.shortcuts import render
from django.views.decorators.http import require_GET

from .forms import FibonacciForm, LoginForm
from .services import build_fibonacci_sections


def home(request):
    return render(request, "challenge/home.html")


def fibonacci_view(request):
    sections = None
    form_data = request.GET if request.method == "GET" and request.GET else None
    if request.method == "POST":
        form_data = request.POST

    form = FibonacciForm(form_data)

    if form.is_bound and form.is_valid():
        sections = build_fibonacci_sections(
            start_value=form.cleaned_data["start_date"],
            end_value=form.cleaned_data["end_date"],
        )

    return render(
        request,
        "challenge/fibonacci.html",
        {
            "form": form,
            "sections": sections,
        },
    )


@require_GET
def login_view(request):
    return render(request, "challenge/login.html", {"form": LoginForm()})


@require_GET
def javascript_view(request):
    """Original browser-side exercise: calculation happens entirely in JavaScript."""
    return render(request, "challenge/javascript.html")


@require_GET
def cli_exercise_view(request):
    """Landing page for the Django equivalent of the PHP CLI exercise."""
    return render(request, "challenge/cli_exercise.html")
