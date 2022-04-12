from sre_parse import CATEGORIES
from django.utils.timezone import datetime
from django.http import HttpResponse
from django.shortcuts import redirect, render

from evaluation.models import UserVideoJunction, Video
from evaluation.utils import Recommendations
import pandas as pd

ALPHA_VALUES = [0, 0.25, 0.5, 0.75, 1.0]
CATEGORIES = ['Loops', 'Conditionals', 'Arrays']
TOTAL_TRIALS = len(ALPHA_VALUES) * len(CATEGORIES)
TRIAL_TIME = 4  # minutes


def home(request):
    return render(request, 'evaluation/home.html', {'date': datetime.now()})


def get_video_pk_by_id(video_id):
    videos = Video.objects.all()
    for i, v in enumerate(videos):
        if v.video_id == video_id:
            return i
    return -1


def get_recommendation_object(user_id):
    video_df = pd.DataFrame(Video.objects.all().values())
    ratings_df = pd.DataFrame(UserVideoJunction.objects.all().values())
    return Recommendations(user_id=user_id,
                           df=video_df, ratings_df=ratings_df)


def get_next_video_to_rate(user_id):
    num_videos = len(Video.objects.all())
    latest_video = UserVideoJunction.objects.filter(
        user_id=user_id).order_by('-pk').first()
    if latest_video is None:
        return 0
    else:
        next_video_id = get_video_pk_by_id(latest_video.video.pk) + 1
        return next_video_id if next_video_id < num_videos else -1


def rate_videos(request, pk=None):
    if request.method == 'POST':
        if pk is not None:
            videos = Video.objects.all()
            video = videos[pk]
            rating = request.POST['rating']
            user = request.user
            uvj, created = UserVideoJunction.objects.update_or_create(
                user=user, video=video, defaults={'rating': rating})
            uvj.save()
            return redirect('rate_videos', pk=pk+1)
        else:
            return redirect('home')
    else:
        if pk is None:
            next_id = get_next_video_to_rate(request.user.id)
            return redirect('rate_videos', pk=next_id)
        done = False
        video = None
        current_id = pk
        try:
            videos = Video.objects.all()
            video = videos[current_id]
        except IndexError:
            done = True
        return render(request, 'evaluation/rate_videos.html', {'video': video, 'done': done, 'next': current_id + 1, 'prev': current_id - 1, 'total': len(videos) - 1})


def get_recs(request):
    recs = get_recommendation_object(request.user.id)
    seed_video_id = 'g8GcFboF2rM'
    all_recs = recs.get_recommendations(seed_video_id)
    videos = [(rec['video_id'], rec['ranking']) for rec in all_recs]
    return render(request, 'evaluation/get_recs.html', {'videos': videos, 'seed_video_id': seed_video_id})


def evaluate(request, trial_id=None):
    recs = get_recommendation_object(request.user.id)
    # for all alpha values in ALPHA_VALUES and all categories in CATEGORIES
    # ask user to rate top 5 videos given a question for TRIAL_TIME minutes
    # randomize the order of trials
    # save to database
    next_trial = trial_id if trial_id is not None else 0
    # generate a diuct of all possible combinations of alpha and categories and then select by id passed to url
    return render(request, 'evaluation/evaluate.html', {'trial_id': next_trial, 'next': next_trial + 1, 'prev': next_trial - 1, 'total': TOTAL_TRIALS})
