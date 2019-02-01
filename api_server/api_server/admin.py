from django.contrib import admin
from api_server.models.level import Level
from api_server.models.evaluation import Evaluation
from api_server.models.submission import Submission

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'score', 'no_stations', 'no_evaluations')


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'score', 'datetime')
    list_filter = ('user', 'level', 'datetime')
    ordering = ['datetime']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'score', 'datetime')
    list_filter = ('user', 'level', 'datetime')
    ordering = ['datetime']
