from django.contrib import admin

from .models import Choice, Question


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    list_display = ["question_text", "pub_date", "end_date"]
    list_filter = ["pub_date"]
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date", "end_date"],
                              "classes": ["collapse"]}),
    ]
    inlines = [ChoiceInline]
    search_fields = ["question_text"]


admin.site.register(Question, QuestionAdmin)
