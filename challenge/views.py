from django.shortcuts import render

from .forms import FibonacciForm, LoginForm
from .services import build_fibonacci_sections


def home(request):
    return render(request, "challenge/home.html")


def fibonacci_view(request):
    sections = None
    form = FibonacciForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
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


def login_view(request):
    return render(request, "challenge/login.html", {"form": LoginForm()})
