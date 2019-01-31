from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError

from api_server.models.level import Level
import api_server.level
import api_server.evaluation
import api_server.evaluators.plane_quadratic as epc

import json


@login_required
@require_http_methods(['POST'])
def eval_level(request, *args, **kwargs):
    if not api_server.level.is_level_open(request.user, kwargs['id']):
        raise PermissionDenied('Level not opened')

    level = Level.objects.get(id=kwargs['id'])
    done_evaluations = api_server.evaluation.no_evaluations(request.user, level)
    if level.no_evaluations > 0 and done_evaluations >= level.no_evaluations:
        raise PermissionDenied('Reached limit of evaluations!')

    nodes = json.loads(level.graph)['nodes'].values()
    nodes = [epc.City(node[0], node[1]) for node in nodes]

    data = json.loads(request.body.decode('utf-8'))
    stations = [epc.Station(s['x'], s['y']) for s in data]

    if len(stations) != level.no_stations:
        raise ValidationError('Invalid number od stations!')

    score = epc.error(nodes, stations)

    return JsonResponse({'score': score})


@login_required
@require_http_methods(['POST'])
def submit_level(request, *args, **kwargs):
    if kwargs['id'] != next_level(user):
        raise PermissionDenied('Level not opened for submission')

    return JsonResponse({'score': kwargs['id']})
