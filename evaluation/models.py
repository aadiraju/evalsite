from pyexpat import model
from django.conf import settings
from django.db import models


# Create your models here.
class Video(models.Model):
    video_id = models.CharField(
        max_length=11, null=False, blank=True, primary_key=True)
    title = models.TextField(db_index=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=False)
    publish_date = models.CharField(max_length=50, null=True, blank=False)
    view_count = models.IntegerField(null=False, blank=False, default=0)
    like_count = models.IntegerField(null=False, blank=False, default=0)
    comment_count = models.IntegerField(null=False, blank=False, default=0)
    youtube_category = models.CharField(max_length=50, null=True, blank=False)
    associated_categories = models.CharField(
        max_length=500, null=True, blank=False)
    vls = models.FloatField(null=True, blank=False, default=0)

    def __str__(self):
        return self.video_id


class UserVideoJunction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='video_junctions', db_index=True)
    video = models.ForeignKey(
        Video, on_delete=models.CASCADE, related_name='user_junctions', db_index=True)
    rating = models.IntegerField(null=True)

    class Meta:
        unique_together = ('user', 'video')


class Question(models.Model):
    question_text = models.TextField(null=True, blank=False)
    category = models.CharField(
        max_length=500, null=True, blank=False)


class TrialData(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='trial_data', db_index=True)
    trial_number = models.IntegerField(null=True, blank=False)
    alpha_value = models.FloatField(null=True, blank=False)
    time_taken = models.IntegerField(null=True)
    video_rankings = models.JSONField(null=True)

    class Meta:
        unique_together = ('user', 'trial_number')


class UserConsent(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    consent = models.BooleanField(null=False, blank=False)


class UserFeedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='user_feedback', db_index=True)
    feedback = models.TextField(null=True, blank=False)
