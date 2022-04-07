from django.utils.timezone import datetime
from django.http import HttpResponse
from django.shortcuts import redirect, render

from evaluation.models import UserVideoJunction, Video
from evaluation.utils import Recommendations
import pandas as pd


def home(request):
    return render(request, 'evaluation/home.html', {'date': datetime.now()})


def rate_videos(request, pk):
    if request.method == 'POST':
        videos = Video.objects.all()
        video = videos[pk]
        rating = request.POST['rating']
        user = request.user
        uvj = UserVideoJunction.objects.create(
            user=user, video=video, rating=rating)
        uvj.save()
        return redirect('rate_videos', pk=pk+1)
    else:
        done = False
        video = None
        try:
            videos = Video.objects.all()
            video = videos[pk]
        except IndexError:
            done = True
        return render(request, 'evaluation/rate_videos.html', {'video': video, 'done': done, 'next': pk + 1, 'prev': pk - 1, 'total': len(videos) - 1})


def get_recs(request):
    video_df = pd.DataFrame(Video.objects.all().values())
    ratings_df = pd.DataFrame(UserVideoJunction.objects.all().values())
    recs = Recommendations(user_id=request.user.id,
                           df=video_df, ratings_df=ratings_df)
    seed_video_id = 'g8GcFboF2rM'
    all_recs = recs.get_recommendations(seed_video_id)
    videos = [(rec['video_id'], rec['ranking']) for rec in all_recs]
    return render(request, 'evaluation/get_recs.html', {'videos': videos, 'seed_video_id': seed_video_id})
