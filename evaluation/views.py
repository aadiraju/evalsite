from django.utils.timezone import datetime
from django.http import HttpResponse
from django.shortcuts import render


def home(request):
    return render(request, 'evaluation/home.html', {'date': datetime.now()})
