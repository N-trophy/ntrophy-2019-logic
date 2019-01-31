from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

from api_server.models.level import Level

class Submission(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    level = models.ForeignKey(
        Level,
        on_delete=models.CASCADE
    )
    score = models.DecimalField(max_digits=8, decimal_places=2)
    positions = models.TextField() # Positions of cities, json
    report = models.TextField() # Anything useful
    datetime = models.DateTimeField(default=datetime.now)

    unique_together = (('user', 'level'),)
