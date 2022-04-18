
from django.contrib import admin

# Register your models here.
from .models import UserConsent, UserFeedback, Video, UserVideoJunction, Question, TrialData

admin.site.register(Video)
admin.site.register(UserVideoJunction)
admin.site.register(Question)
admin.site.register(TrialData)
admin.site.register(UserConsent)
admin.site.register(UserFeedback)
