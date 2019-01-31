from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.views import View
from django.template import loader, RequestContext, Library
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required

import json
from api_server.models import Level

register = Library()

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

def level_class(next_level, level_id):
    if next_level > level_id:
        return "w3-red"
    elif next_level == level_id:
        return "w3-white"
    else:
        return "w3-dark-gray"

def level_status(next_level, level):
    if next_level > level.id:
        return "Skóre: 3"
    elif next_level == level.id:
        return "Otevřeno"
    else:
        return "Zatím uzavřeno"

@login_required
def index(request, *args, **kwargs):
    template = loader.get_template('index.html')
    next_level = 3
    levels = list(map(lambda l: { 'id': l.id, 'status': level_status(next_level, l), 'class': level_class(next_level, l.id) }, Level.objects.order_by('id')))

    context = {
        'levels': levels,
        'next_level': next_level
    }
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
