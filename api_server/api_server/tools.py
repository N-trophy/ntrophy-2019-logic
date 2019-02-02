from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

import json

@login_required
@require_http_methods(['POST'])
@permission_required('add_user', 'change_user')
def user_create(request, *args, **kwargs):
    body = request.body.decode('utf-8')
    users = []
    for line in body.split('\n'):
        login, teamname, email = line.strip().split(',')

        users.append(User(
            username=login,
            first_name=teamname,
            email=email,
            password=User.objects.make_random_password(),
            is_active=True,
        ))

    User.objects.bulk_create(users)

    return JsonResponse(
        {user.username: user.password for user in users}
    )
