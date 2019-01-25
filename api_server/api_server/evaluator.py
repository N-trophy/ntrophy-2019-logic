from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods

from api_server.models import Level

@require_http_methods(["GET", "POST"])
def eval_level(request, *args, **kwargs):
        return JsonResponse({'score': kwargs['id']})
