from django.contrib import admin

from .models import Answer, GuardrailLog, LawReference, LearnerProfile, Question


@admin.register(LawReference)
class LawReferenceAdmin(admin.ModelAdmin):
    list_display = ("article_number", "paragraph", "title", "language", "last_updated")
    search_fields = ("article_number", "title", "text")
    list_filter = ("language", "last_updated")


admin.site.register(LearnerProfile)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(GuardrailLog)

