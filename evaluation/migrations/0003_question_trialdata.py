# Generated by Django 4.0.3 on 2022-04-13 05:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('evaluation', '0002_video_vls_alter_video_duration'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField(null=True)),
                ('category', models.CharField(max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TrialData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trial_number', models.IntegerField(null=True)),
                ('alpha_value', models.FloatField(null=True)),
                ('time_taken', models.IntegerField(null=True)),
                ('video_rankings', models.JSONField(null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trial_data', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'trial_number')},
            },
        ),
    ]
