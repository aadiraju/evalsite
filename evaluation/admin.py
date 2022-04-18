
from django.contrib import admin

# Register your models here.
from .models import UserConsent, UserFeedback, Video, UserVideoJunction, Question, TrialData


class UserVideoJunctionAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'rating')
    list_filter = ('user', 'video', 'rating')
    search_fields = ('user', 'video')


class TrialDataAdmin(admin.ModelAdmin):
    list_filter = ('user', 'alpha_value', 'trial_number')


admin.site.register(Video)
admin.site.register(UserVideoJunction, UserVideoJunctionAdmin)
admin.site.register(Question)
admin.site.register(TrialData, TrialDataAdmin)
admin.site.register(UserConsent)
admin.site.register(UserFeedback)
