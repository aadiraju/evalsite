from django.utils.timezone import datetime
from django.http import HttpResponse
from django.shortcuts import redirect, render

from evaluation.models import UserVideoJunction, Video


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
        return render(request, 'evaluation/rate_videos.html', {'video': video, 'done': done, 'current': pk, 'next': pk + 1, 'prev': pk - 1, 'total': len(videos) - 1})
