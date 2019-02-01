from django.contrib import admin
from api_server.models.level import Level
from api_server.models.evaluation import Evaluation
from api_server.models.submission import Submission

admin.site.register(Level)
admin.site.register(Evaluation)
admin.site.register(Submission)
