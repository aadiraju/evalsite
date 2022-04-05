import csv
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db import IntegrityError

import os
from evaluation.models import Video


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--filepath', type=str)

    def handle(self, *args, **options):
        filepath = options['filepath']
        print(f'Importing Videos from CSV @ {filepath}')
        with open(filepath, encoding = 'utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Video.objects.get_or_create(
                    video_id=row['video_id'],
                    title=row['title'],
                    description=row['description'],
                    duration=row['duration'],
                    publish_date=row['publish_date'],
                    view_count=row['view_count'],
                    like_count=row['like_count'],
                    comment_count=row['comment_count'],
                    youtube_category=row['youtube_category'],
                    associated_categories=row['categories'],
                    vls=row['VLS']
                )
