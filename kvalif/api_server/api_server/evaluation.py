from api_server.models import Level, Submission, Evaluation

def no_evaluations(user, level):
    return Evaluation.objects.filter(user=user, level=level).count()

