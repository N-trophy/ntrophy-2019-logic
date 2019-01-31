from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from api_server.models.level import Level
import api_server.level


@login_required
@require_http_methods(['POST'])
def eval_level(request, *args, **kwargs):
    if not api_server.level.is_level_open(request.user, kwargs['id']):
        raise PermissionDenied('Level not opened')

    return JsonResponse({'score': kwargs['id']})


@login_required
@require_http_methods(['POST'])
def submit_level(request, *args, **kwargs):
    if kwargs['id'] != next_level(user):
        raise PermissionDenied('Level not opened for submission')

    return JsonResponse({'score': kwargs['id']})
