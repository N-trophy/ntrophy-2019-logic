from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.views import View
from django.template import loader, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

import json

from api_server.models import Level

def graph(request, *args, **kwargs):
    task_number = kwargs['id']
    try:
        level_object = Level.objects.get(id=task_number)
    except ObjectDoesNotExist:
        raise Http404("Task doesn't exist.")

    data = json.loads(level_object.graph)
    data['nodes'] = [[nodeid]+nodedata for nodeid, nodedata in data['nodes'].items()]
    return JsonResponse(data)

def index(request, *args, **kwargs):
    template = loader.get_template('index.html')
    levels = Level.objects.order_by('id')
    print(levels)
    context = {
        'levels': levels
    }
    return HttpResponse(template.render(context, request))

def level(request, *args, **kwargs):
    template = loader.get_template('level.html')
    context = {
        'level_id': kwargs['id']
    }
    return HttpResponse(template.render(context, request))

def graph_js(request, *args, **kwargs):
    template = loader.get_template('graph.js')
    context = {
        'level_id': kwargs['id']
    }
    return HttpResponse(template.render(context, request))
