from django.db import models
from django import forms
import json
import os

def path_and_rename(instance, filename):
    upload_to = 'levels'
    ext = filename.split('.')[-1]
    # get filename
    filename = '{}.{}'.format(instance.pk, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)

class Level(models.Model):
    EVAL_FUNCTIONS = [('QUADRATIC', 'quadratic'), ('LINEAR', 'linear')]

    id = models.PositiveIntegerField(primary_key=True)
    no_stations = models.PositiveIntegerField(default=1)
    score = models.CharField(max_length=16, choices=EVAL_FUNCTIONS, default='1')
    graph = models.TextField()
    intro_text = models.TextField()

    def validate_graph_data(graph):
        if False:
            # TODO Add graph validation
            raise ValueError()
