from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Post(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )
    text = models.TextField()
    published = models.DateTimeField(default=datetime.now)
