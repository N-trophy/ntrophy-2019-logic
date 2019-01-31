from django.db.models import Max
from api_server.models import Level, Submission

def next_level(user):
    return Submission.objects.filter(user=user).\
        aggregate(Max('level'))['level__max'] + 1

def done_levels(user):
    return {
        submission.level.id: submission \
        for submission in Submission.objects.filter(user=user)
    }
