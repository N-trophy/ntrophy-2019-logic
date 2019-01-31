from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from api_server.models.level import Level


@login_required
@require_http_methods(["GET", "POST"])
def eval_level(request, *args, **kwargs):
        return JsonResponse({'score': kwargs['id']})


@login_required
@require_http_methods(["GET", "POST"])
def submit_level(request, *args, **kwargs):
        return JsonResponse({'score': kwargs['id']})
