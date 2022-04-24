import csv
import pandas as pd
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db import IntegrityError

import os
from evaluation.models import Video, Question, TrialData, UserVideoJunction
from accounts.models import MyUser
from evaluation.views import TRIAL_CONDITIONS


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--filepath', type=str)

    def handle(self, *args, **options):
        filepath = options['filepath']
        print(f'Exporting Trial Data into @ {filepath}')
        df = pd.DataFrame(list(TrialData.objects.all().values()))
        df['category'] = df.apply(
        lambda row: TRIAL_CONDITIONS[row['trial_number']]['category'], axis=1)
        df.to_csv(filepath, index=False)


