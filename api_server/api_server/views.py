from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.views import View
from django.template import loader, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

import json

from api_server.models import LevelFile

def graph(request, *args, **kwargs):
    task_number = kwargs['id']
    try:
        level_object = LevelFile.objects.get(id=task_number)
    except ObjectDoesNotExist:
        raise Http404("Task doesn't exist.")

    with level_object.data.open("r") as f:
        data = json.loads(f.read())

    data['nodes'] = [[nodeid]+nodedata for nodeid, nodedata in data['nodes'].items()]
    return JsonResponse(data)

def index(request, *args, **kwargs):
    template = loader.get_template('index.html')
    levels = LevelFile.objects.order_by('id')
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
