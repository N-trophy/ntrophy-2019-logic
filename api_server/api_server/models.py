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

class LevelFile(models.Model):
    data = models.FileField(upload_to=path_and_rename)
    id = models.PositiveIntegerField(primary_key=True)

    def validate_graph_data(graph):
        if False:
            # TODO Add graph validation
            raise ValueError()

    def save(self, *args, **kwargs):
        json_text_data = self.data.read().decode('utf-8')
        try:
            json_data = json.loads(json_text_data)
            LevelFile.validate_graph_data(json_data)
            super(LevelFile, self).save(*args, **kwargs)
        except ValueError:
            raise forms.ValidationError("Invalid JSON format.")