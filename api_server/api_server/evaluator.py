from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError

from api_server.models.level import Level
from api_server.models.evaluation import Evaluation
from api_server.models.submission import Submission
import api_server.level
import api_server.evaluation
import api_server.evaluators.plane as ep
import api_server.evaluators.graph as eg

import json
import math


def error_plane(level, stations, graph=None):
    if graph is None:
        graph = json.loads(level.graph)

    nodes = graph['nodes'].values()
    nodes = [ep.City(node[0], node[1]) for node in nodes]

    stations = [ep.Station(s['x'], s['y']) for s in stations]

    if level.score == 'QUADRATIC':
        return ep.quadratic_error(nodes, stations)
    else:
        return ep.linear_error(nodes, stations)


def euclid_distance(a: (float, float), b: (float, float)) -> float:
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)


def error_graph(level, stations, graph=None):
    if graph is None:
        graph = json.loads(level.graph)

    nodes = {id: eg.Node(weight) for (id, (x, y, weight)) in graph['nodes'].items()}
    edges = [eg.Edge(start, end, weight) for start, end, weight in graph['edges']]
    s = []
    for st in stations:
        nodea, nodeb, x, y = (st['edge_a'], st['edge_b'], st['x'], st['y'])
        nodes_dist = euclid_distance(graph['nodes'][nodea], graph['nodes'][nodeb])
        dista = euclid_distance(graph['nodes'][nodea], (x, y))
        distb = euclid_distance(graph['nodes'][nodeb], (x, y))
        s.append(eg.Station(nodea, nodeb, dista/(dista+distb), distb/(dista+distb)))

    g = eg.Graph(nodes, edges)
    return eg.error(g, s)


def error(level, stations) -> float:
    graph = json.loads(level.graph)

    if len(graph['edges']) == 0:
        # Plane
        return error_plane(level, stations, graph)
    else:
        # Graph
        return error_graph(level, stations, graph)


@login_required
@require_http_methods(['POST'])
def eval_level(request, *args, **kwargs):
    if not api_server.level.is_level_open(request.user, kwargs['id']):
        raise PermissionDenied('Level not opened')

    level = Level.objects.get(id=kwargs['id'])
    done_evaluations = api_server.evaluation.no_evaluations(request.user, level)
    if level.no_evaluations > 0 and done_evaluations >= level.no_evaluations:
        raise PermissionDenied('Reached limit of evaluations!')

    # TODO: add another limit of evaluations?

    body = request.body.decode('utf-8')
    stations = json.loads(body)

    if len(stations) != level.no_stations:
        raise ValidationError('Invalid number of stations!')

    score = round(error(level, stations), 2)

    evaluation = Evaluation(
        user=request.user,
        level=level,
        score=score,
        positions=body,
        report='ok',
    )
    evaluation.save()

    return JsonResponse({
        'score': score,
        'remaining': api_server.level.evals_remaining(request.user, level), # -1 if no limit
    })


@login_required
@require_http_methods(['POST'])
def submit_level(request, *args, **kwargs):
    if kwargs['id'] != api_server.level.next_level(request.user):
        raise PermissionDenied('Level not opened for submission')

    level = Level.objects.get(id=kwargs['id'])
    body = request.body.decode('utf-8')
    stations = json.loads(body)

    if len(stations) != level.no_stations:
        raise ValidationError('Invalid number of stations!')

    score = error(level, stations)

    evaluation = Submission(
        user=request.user,
        level=level,
        score=score,
        positions=body,
        report='ok',
    )
    evaluation.save()

    return JsonResponse({
        'score': score,
    })
