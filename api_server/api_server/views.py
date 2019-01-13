from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.views import View

class Graph(View):
    def get(self, request, *args, **kwargs):
        task_number = request.GET.get('task_number')
        if not task_number or int(task_number) > 8:
            raise Http404("Task doesn't exist.")
        return render_to_response("graph_{}.json".format(task_number), content_type='application/json')