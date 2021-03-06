from django.utils.timezone import datetime
from django.http import HttpResponse
from django.shortcuts import redirect, render

from evaluation.models import Question, TrialData, UserConsent, UserFeedback, UserVideoJunction, Video
from evaluation.utils import Recommendations
import pandas as pd
import random
import secrets

ALPHA_VALUES = [0, 0.25, 0.5, 0.75, 1.0]
CATEGORIES = ['Loops', 'Conditional', 'Array']
TOTAL_TRIALS = len(ALPHA_VALUES) * len(CATEGORIES)
TRIAL_TIME = 4  # minutes


def generate_trial_conditions():
    conditions = []
    trial_number = 0
    for alpha in ALPHA_VALUES:
        for category in CATEGORIES:
            questions = Question.objects.filter(category__contains=category)
            question = questions[trial_number % len(questions)]
            conditions.append(
                {'alpha': alpha, 'category': category, 'trial_number': trial_number, 'question': question})
            trial_number += 1
    return conditions


TRIAL_CONDITIONS = generate_trial_conditions()


def get_seed_video_by_category(category, user_id):
    # select their highest-rated video from the category or a random video in the category
    videos = Video.objects.filter(associated_categories__contains=category)
    uvjs = UserVideoJunction.objects.filter(user_id=user_id, video__in=videos)
    if len(uvjs) > 0:
        uvj_list = sorted(list(uvjs), key=lambda x: x.rating, reverse=True)
        half_uvj_list = uvj_list[: len(uvj_list)//2]
        if len(uvj_list) > 1:
            return secrets.choice(half_uvj_list).video.video_id
        else:
            return uvj_list[0].video.video_id
    else:
        random_idx = random.randint(0, len(videos) - 1)
        return videos[random_idx].video_id


def home(request):
    if request.user.is_authenticated:
        return render(request, 'evaluation/home.html')
    return redirect('register')


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
        return next_video_id if next_video_id < num_videos else num_videos


def rate_videos(request, pk=None):
    if request.method == 'POST':
        if pk is not None:
            video_qset = Video.objects.all()
            videos = list(video_qset)
            # since we set the seed as user id, every user will have a uniquely shuffled order
            random.Random(request.user.pk).shuffle(videos)
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
            video_qset = Video.objects.all()
            videos = list(video_qset)
            # since we set the seed as user id, every user will have a uniquely shuffled order
            random.Random(request.user.pk).shuffle(videos)
            video = videos[current_id]
        except IndexError:
            done = True
        return render(request, 'evaluation/rate_videos.html', {'video': video, 'done': done, 'next': current_id + 1, 'prev': current_id - 1, 'total': len(videos)})


def get_recs(request):
    recs = get_recommendation_object(request.user.id)
    seed_video_id = 'g8GcFboF2rM'
    all_recs = recs.get_recommendations(seed_video_id)
    videos = [(rec['video_id'], rec['ranking']) for rec in all_recs]
    return render(request, 'evaluation/get_recs.html', {'videos': videos, 'seed_video_id': seed_video_id})


def get_next_trial(user_id):
    latest_trial = TrialData.objects.filter(
        user=user_id).order_by('-trial_number').first()
    if latest_trial is None:
        return 0
    else:
        next_trial = latest_trial.trial_number + 1
        return next_trial if next_trial < TOTAL_TRIALS else TOTAL_TRIALS


def study_info(request):
    return render(request, 'evaluation/study_info.html')


def evaluate(request, trial_id=None):
    if request.method == 'POST':
        if trial_id is not None:
            form_data = request.POST
            trial_id = int(trial_id)
            alpha = TRIAL_CONDITIONS[trial_id]['alpha']
            video_ids = form_data.getlist('video')
            predicted_rankings = form_data.getlist('predicted_ranking')
            time_taken = form_data.get('time_taken')
            video_rankings = dict(zip(video_ids, predicted_rankings))
            rankings = {}
            for video_id in video_ids:
                # default 0 if not found
                ranking = form_data.get(f'rating-{video_id}', 0)
                rankings[video_id] = {
                    'user_rating': ranking, 'predicted_rating': video_rankings[video_id]}
            user = request.user

            trial_data, created = TrialData.objects.update_or_create(
                user=user, trial_number=trial_id,
                defaults={'alpha_value': alpha, 'time_taken': time_taken, 'video_rankings': rankings})

            return redirect('evaluate', trial_id=trial_id+1)
        else:
            return redirect('home')
    else:
        if trial_id is None:
            next_trial = get_next_trial(request.user.id)
            return redirect('evaluate', trial_id=next_trial)
        else:
            rec = get_recommendation_object(request.user.id)
            done = False
            trial_num = trial_id
            if trial_num >= TOTAL_TRIALS:
                done = True
                alpha = 0
                category = ''
                question = ''
                videos = []
            else:
                condition_data = TRIAL_CONDITIONS[trial_num]
                alpha = condition_data['alpha']
                category = condition_data['category']
                question = condition_data['question']
                recs = rec.get_recommendations(
                    seed_video=get_seed_video_by_category(category, request.user.id), alpha=alpha)
                videos = [(rec['video_id'], rec['ranking']) for rec in recs]
            return render(request, 'evaluation/evaluate.html',
                          {'trial_id': trial_num, 'next': trial_num + 1, 'prev': trial_num - 1,
                           'total': TOTAL_TRIALS, 'question': question, 'videos': videos, 'category': category, 'alpha': alpha, 'done': done, 'time': TRIAL_TIME})


def submit_feedback(request):
    if request.method == 'POST':
        form_data = request.POST
        feedback = form_data.get('feedback')
        user = request.user
        feedback_data = UserFeedback(user=user, feedback=feedback)
        feedback_data.save()
        return redirect('home')
    else:
        return redirect('home')


def submit_consent(request):
    if request.method == 'POST':
        form_data = request.POST
        user = request.user
        if 'consent' in form_data:
            consent_data = UserConsent(user=user, consent=True)
        else:
            consent_data = UserConsent(user=user, consent=False)
        consent_data.save()
        return redirect('home')
    else:
        return render(request, 'evaluation/consent.html')
