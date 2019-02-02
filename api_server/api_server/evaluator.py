from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views import View
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

from api_server.models.level import Level
from api_server.models.evaluation import Evaluation
from api_server.models.submission import Submission
import api_server.level
import api_server.evaluation
import api_server.evaluators.plane as ep
import api_server.evaluators.graph as eg

import json
import math
import traceback
from datetime import datetime

QUALIFICATION_END = timezone.make_aware(datetime(2019, 2, 25, 0, 0, 0))

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

def is_edge_in_graph(graph, nodea, nodeb):
    for e in graph['edges']:
        if (e[0] == nodea and e[1] == nodeb) or (e[0] == nodeb and e[1] == nodea):
            return True
    return False

def error_graph(level, stations, graph=None):
    if graph is None:
        graph = json.loads(level.graph)

    nodes = {id: eg.Node(weight) for (id, (x, y, weight)) in graph['nodes'].items()}
    edges = [eg.Edge(start, end, weight) for start, end, weight in graph['edges']]
    s = []
    for st in stations:
        nodea, nodeb, x, y = (st['edge_a'], st['edge_b'], st['x'], st['y'])

        if not is_edge_in_graph(graph, nodea, nodeb):
            raise ValidationError('There is no such edge in graph!')

        nodes_dist = euclid_distance(graph['nodes'][nodea], graph['nodes'][nodeb])
        dista = euclid_distance(graph['nodes'][nodea], (x, y))
        distb = euclid_distance(graph['nodes'][nodeb], (x, y))
        s.append(eg.Station(nodea, nodeb, dista/(dista+distb), distb/(dista+distb)))

    g = eg.Graph(nodes, edges)
    return eg.error(g, s)


def error(level, stations) -> float:
    graph = json.loads(level.graph)

    for station in stations:
        station['x'] = round(station['x'], 2)
        station['y'] = round(station['y'], 2)

    if len(graph['edges']) == 0:
        # Plane
        e = error_plane(level, stations, graph)
    else:
        # Graph
        e = error_graph(level, stations, graph)

    return round(e, 2)


@login_required
@require_http_methods(['POST'])
def eval_level(request, *args, **kwargs):
    if not api_server.level.is_level_open(request.user, kwargs['id']):
        return HttpResponseForbidden('Level not opened!')

    if timezone.now() >= QUALIFICATION_END:
        return HttpResponseForbidden('Qualification ended!')

    try:
        level = Level.objects.get(id=kwargs['id'])
    except api_server.models.level.Level.DoesNotExist:
        return HttpResponseNotFound('Level not found')

    done_evaluations = api_server.evaluation.no_evaluations(request.user, level)
    if level.no_evaluations > 0 and done_evaluations >= level.no_evaluations:
        return HttpResponseForbidden('Reached limit of evaluations!')

    # TODO: add another limit of evaluations?

    body = request.body.decode('utf-8')
    stations = json.loads(body)

    if len(stations) != level.no_stations:
        return HttpResponseBadRequest('Invalid number of stations!')

    evaluation = Evaluation(
        user=request.user,
        level=level,
        positions=body,
    )

    try:
        evaluation.score = error(level, stations)
        evaluation.report = 'ok'
    except ValidationError as e:
        evaluation.report = 'Validation Error:\n' + traceback.format_exc()
        return HttpResponseBadRequest(str(e))
    except Exception:
        evaluation.report = traceback.format_exc()
        raise
    finally:
        evaluation.save()

    return JsonResponse({
        'score': evaluation.score,
        'remaining': api_server.level.evals_remaining(request.user, level), # -1 if no limit
    })


@login_required
@require_http_methods(['POST'])
def submit_level(request, *args, **kwargs):
    if kwargs['id'] != api_server.level.next_level(request.user):
        return HttpResponseForbidden('Level not opened for submission!')

    if timezone.now() >= QUALIFICATION_END:
        return HttpResponseForbidden('Qualification ended!')

    try:
        level = Level.objects.get(id=kwargs['id'])
    except api_server.models.level.Level.DoesNotExist:
        return HttpResponseNotFound('Level not found')

    body = request.body.decode('utf-8')
    stations = json.loads(body)

    if len(stations) != level.no_stations:
        return HttpResponseBadRequest('Invalid number of stations!')

    evaluation = Submission(
        user=request.user,
        level=level,
        positions=body,
    )

    try:
        evaluation.score = error(level, stations)
        evaluation.report = 'ok'
    except ValidationError as e:
        evaluation.report = 'Validation Error:\n' + traceback.format_exc()
        return HttpResponseBadRequest(str(e))
    except Exception:
        evaluation.report = traceback.format_exc()
        raise
    finally:
        evaluation.save()

    return JsonResponse({
        'score': evaluation.score,
    })
