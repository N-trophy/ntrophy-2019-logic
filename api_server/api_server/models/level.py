from django.db import models
from django import forms
import json
import os

class Level(models.Model):
    EVAL_FUNCTIONS = [('QUADRATIC', 'quadratic'), ('LINEAR', 'linear')]

    id = models.PositiveIntegerField(primary_key=True)
    no_stations = models.PositiveIntegerField(default=1)
    score = models.CharField(max_length=16, choices=EVAL_FUNCTIONS, default='1')
    graph = models.TextField()
    intro_text = models.TextField(default='')
    no_evaluations = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)
