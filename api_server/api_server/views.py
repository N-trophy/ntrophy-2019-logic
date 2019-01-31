from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.views import View
from django.template import loader, RequestContext, Library
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.http import Http404
from django.core.exceptions import PermissionDenied

from django.contrib.auth.decorators import login_required

import json
from api_server.models import Level
import api_server.level

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

def level_status(next_level, level, submission=None):
    if next_level > level.id and submission is not None:
        return "Skóre: %d" % (submission.score)
    elif next_level == level.id:
        return "Otevřeno"
    else:
        return "Zatím uzavřeno"

@login_required
def index(request, *args, **kwargs):
    template = loader.get_template('index.html')
    done_levels = api_server.level.done_levels(request.user)
    next_level = max(done_levels.keys())+1
    levels = list(map(lambda l: {
        'id': l.id,
        'status': level_status(next_level, l, done_levels.get(l.id)),
        'class': level_class(next_level, l.id)
    }, Level.objects.order_by('id')))

    context = {
        'levels': levels,
        'next_level': next_level,
        'name': request.user.get_full_name()
    }
    return HttpResponse(template.render(context, request))

@login_required
def level(request, *args, **kwargs):
    if not api_server.level.is_level_open(request.user, kwargs['id']):
        raise PermissionDenied("Task not opened.")

    template = loader.get_template('level.html')
    level = Level.objects.get(id=kwargs['id'])
    context = {
        'level_id': kwargs['id'],
        'level': level
    }
    return HttpResponse(template.render(context, request))

@login_required
def graph_js(request, *args, **kwargs):
    template = loader.get_template('graph.js')
    context = {
        'level_id': kwargs['id']
    }
    return HttpResponse(template.render(context, request))
