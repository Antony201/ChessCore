from django.contrib import admin

from core.feedback.models import Feedback, Message, File
from django_paranoid.admin import ParanoidAdmin


class FeedbackAdmin(ParanoidAdmin):
    pass

class MessageAdmin(ParanoidAdmin):
    pass


admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(File)
