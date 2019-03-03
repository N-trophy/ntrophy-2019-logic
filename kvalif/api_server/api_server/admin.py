from django.contrib import admin
from api_server.models import Level, Evaluation, Submission, Post


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'score', 'no_stations', 'no_evaluations',
                    'no_submitted_teams', 'no_evaluated_teams')

    def no_submitted_teams(slf, obj):
        return Submission.objects.filter(level=obj.id).count()

    def no_evaluated_teams(slf, obj):
        return Evaluation.objects.filter(level=obj.id).values_list('user').\
               distinct().count()


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'score', 'datetime', 'report')
    list_filter = ('user', 'level', 'datetime', 'report')
    ordering = ['-datetime']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'score', 'datetime', 'report')
    list_filter = ('user', 'level', 'datetime', 'report')
    ordering = ['-datetime']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'published', 'text')
    list_filter = ('id', 'author', 'published')
    ordering = ['published']
