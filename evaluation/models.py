from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Video(models.Model):
    video_id = models.CharField(max_length=11, null=False, blank=True, primary_key=True)
    title = models.TextField(db_index=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    duration = models.CharField(max_length=50, null=True, blank=False)
    publish_date = models.CharField(max_length=50, null=True, blank=False)
    view_count = models.IntegerField(null=False, blank=False, default=0)
    like_count = models.IntegerField(null=False, blank=False, default=0)
    comment_count = models.IntegerField(null=False, blank=False, default=0)
    youtube_category = models.CharField(max_length=50, null=True, blank=False)
    associated_categories = models.CharField(max_length=500, null=True, blank=False)

    def __str__(self):
        return self.video_id


class UserVideoJunction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_junctions', db_index=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='user_junctions', db_index=True)
    rating = models.IntegerField(null=True)

    class Meta:
        unique_together = ('user', 'video')