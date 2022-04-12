from django.urls import path
from evaluation import views

urlpatterns = [
    path('', views.home, name='home'),
    path('get_recs/', views.get_recs, name='get_recs'),
    path('rate_videos/<int:pk>', views.rate_videos, name='rate_videos'),
    path('rate_videos/', views.rate_videos, name='rate_videos'),
]
