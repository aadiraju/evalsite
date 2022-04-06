from django.urls import path
from evaluation import views

urlpatterns = [
    path('', views.home, name='home'),
    path('rate_videos/<int:pk>', views.rate_videos, name='rate_videos'),
]
