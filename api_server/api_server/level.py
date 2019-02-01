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
