from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.views import View
from django.template import loader, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

import json

from api_server.models.level import Level

@login_required
def graph(request, *args, **kwargs):
    task_number = kwargs['id']
    try:
        level_object = Level.objects.get(id=task_number)
    except ObjectDoesNotExist:
        raise Http404("Task doesn't exist.")

    data = json.loads(level_object.graph)
    data['nodes'] = [[nodeid]+nodedata for nodeid, nodedata in data['nodes'].items()]
    return JsonResponse(data)

@login_required
def index(request, *args, **kwargs):
    template = loader.get_template('index.html')
    levels = Level.objects.order_by('id')
    context = {
        'levels': levels
    }
    return HttpResponse(template.render(context, request))

@login_required
def team(request, *args, **kwargs):
    template = loader.get_template('team.html')
    context = {}
    return HttpResponse(template.render(context, request))

@login_required
def level(request, *args, **kwargs):
    template = loader.get_template('level.html')
    context = {
        'level_id': kwargs['id']
    }
    return HttpResponse(template.render(context, request))

@login_required
def graph_js(request, *args, **kwargs):
    template = loader.get_template('graph.js')
    context = {
        'level_id': kwargs['id']
    }
    return HttpResponse(template.render(context, request))
