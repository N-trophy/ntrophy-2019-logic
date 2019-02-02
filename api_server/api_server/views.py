from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.views import View
from django.template import loader, RequestContext, Library
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.utils import timezone

import json
import csv

from api_server.models import Level
from api_server.models import Post
import api_server.level

register = Library()

def level_class(next_level, level_id):
    if next_level > level_id:
        return "w3-red"
    elif next_level == level_id:
        return "w3-white"
    else:
        return "w3-dark-gray"

def level_status(next_level, level, submission=None):
    if next_level > level.id and submission is not None:
        return "Chyba: %.2f" % (submission.score)
    elif next_level == level.id:
        return "Otevřeno"
    else:
        return "Zatím uzavřeno"

@login_required
def index(request, *args, **kwargs):
    template = loader.get_template('index.html')
    done_levels = api_server.level.done_levels(request.user)
    if len(done_levels.keys()) > 0:
        next_level = max(done_levels.keys())+1
    else:
        next_level = 1
    levels = list(map(lambda l: {
        'id': l.id,
        'status': level_status(next_level, l, done_levels.get(l.id)),
        'class': level_class(next_level, l.id)
    }, Level.objects.order_by('id')))

    context = {
        'levels': levels,
        'next_level': next_level,
        'name': request.user.get_full_name(),
        'posts': Post.objects.filter(published__lt=timezone.now()).\
                 order_by('-published')[:12],
    }
    return HttpResponse(template.render(context, request))

@login_required
def level(request, *args, **kwargs):
    if not api_server.level.is_level_open(request.user, kwargs['id']):
        return HttpResponseForbidden('Level not opened!')

    template = loader.get_template('level.html')
    level = Level.objects.get(id=kwargs['id'])
    graph = json.loads(level.graph)
    context = {
        'level_id': kwargs['id'],
        'level': level,
        'allow_submit': kwargs['id'] == api_server.level.next_level(request.user),
        'evals_remaining': api_server.level.evals_remaining(request.user, level),
        'weighted_edges': api_server.level.are_edges_weighted(graph),
        'weighted_nodes': api_server.level.are_nodes_weighted(graph),
    }
    return HttpResponse(template.render(context, request))

@login_required
def graph_js(request, *args, **kwargs):
    template = loader.get_template('graph.js')
    context = {
        'level_id': kwargs['id']
    }
    return HttpResponse(template.render(context, request))


@login_required
def data_level(request, *args, **kwargs):
    if not api_server.level.is_level_open(request.user, kwargs['id']):
        return HttpResponseForbidden('Level not opened!')

    response = HttpResponse(content_type='text/csv; charset=utf8')
    response['Content-Disposition'] = 'attachment; filename={0}'.\
        format('level%d.csv' % (kwargs['id']))

    data = csv.writer(response)
    graph = json.loads(Level.objects.get(id=kwargs['id']).graph)
    nodes_weighted = api_server.level.are_nodes_weighted(graph)
    edges_weighted = api_server.level.are_edges_weighted(graph)

    row = ['Type']
    if len(graph['edges']) > 0:
        row.append('Id')
    row += ['X', 'Y']
    if nodes_weighted:
        row.append('Weight')
    data.writerow(row)

    for nname, ndata in graph['nodes'].items():
        row = ['node']
        if len(graph['edges']) > 0:
            row.append(nname)
        row += [ndata[0], ndata[1]]
        if nodes_weighted:
            row.append(ndata[2])
        data.writerow(row)

    data.writerow([])

    if len(graph['edges']) > 0:
        row = ['Type']
        row += ['From', 'To']
        if edges_weighted:
            row.append('Weight')
        data.writerow(row)

    for edge in graph['edges']:
        if edges_weighted:
            data.writerow(['edge', edge[0], edge[1], edge[2]])
        else:
            data.writerow(['edge', edge[0], edge[1]])

    return response
