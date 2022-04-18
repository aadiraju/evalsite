from django.urls import path
from evaluation import views

urlpatterns = [
    path('', views.home, name='home'),
    path('get_recs/', views.get_recs, name='get_recs'),
    path('rate_videos/<int:pk>', views.rate_videos, name='rate_videos'),
    path('rate_videos/', views.rate_videos, name='rate_videos'),
    path('study_info/', views.study_info, name='study_info'),
    path('evaluate/<int:trial_id>', views.evaluate, name='evaluate'),
    path('evaluate/', views.evaluate, name='evaluate'),
    path('submit_feedback/', views.submit_feedback, name='submit_feedback'),
    path('consent/', views.submit_consent, name = 'consent'),
]
