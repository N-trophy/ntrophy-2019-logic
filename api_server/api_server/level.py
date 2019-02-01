from django.db.models import Max
from api_server.models import Level, Submission
import api_server.evaluation

def next_level(user):
    return Submission.objects.filter(user=user,).exclude(score=None).\
        aggregate(Max('level'))['level__max'] + 1

def done_levels(user):
    return {
        submission.level.id: submission \
        for submission in Submission.objects.filter(user=user).exclude(score=None)
    }

def is_level_open(user, level_id):
    done = done_levels(user).keys()
    return level_id in done or level_id-1 in done or level_id == 1

def are_nodes_weighted(graph):
    for ndata in graph['nodes'].values():
        if ndata[2] != 1:
            return True
    return False

def are_edges_weighted(graph):
    for edge in graph['edges']:
        if edge[2] != 1:
            return True
    return False

def evals_remaining(user, level):
    if level.no_evaluations == 0:
        return -1
    else:
        done_evaluations = api_server.evaluation.no_evaluations(user, level)
        return level.no_evaluations-done_evaluations
