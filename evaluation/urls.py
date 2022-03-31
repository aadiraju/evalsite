from django.urls import path
from evaluation import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.home, name='about'),
]
