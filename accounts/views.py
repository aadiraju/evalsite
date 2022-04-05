from django.shortcuts import render
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.urls import reverse
from accounts.forms import SignupForm

# Create your views here.


def register(request):
    if request.method == "GET":
        return render(
            request, "users/register.html",
            {"form": SignupForm}
        )
    elif request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("home"))
        else:
            form = SignupForm()
    return render(request, 'users/register.html', {'form': form})
