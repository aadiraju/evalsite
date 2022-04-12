from django.utils.timezone import datetime
from django.http import HttpResponse
from django.shortcuts import redirect, render

from evaluation.models import UserVideoJunction, Video
from evaluation.utils import Recommendations
import pandas as pd


def home(request):
    return render(request, 'evaluation/home.html', {'date': datetime.now()})


def get_video_pk_by_id(video_id):
    videos = Video.objects.all()
    for i, v in enumerate(videos):
        if v.video_id == video_id:
            return i
    return -1


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
    video_df = pd.DataFrame(Video.objects.all().values())
    ratings_df = pd.DataFrame(UserVideoJunction.objects.all().values())
    recs = Recommendations(user_id=request.user.id,
                           df=video_df, ratings_df=ratings_df)
    seed_video_id = 'g8GcFboF2rM'
    all_recs = recs.get_recommendations(seed_video_id)
    videos = [(rec['video_id'], rec['ranking']) for rec in all_recs]
    return render(request, 'evaluation/get_recs.html', {'videos': videos, 'seed_video_id': seed_video_id})
