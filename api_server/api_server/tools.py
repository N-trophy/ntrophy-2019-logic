from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.mail import send_mass_mail

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

    mails = [
        ('[N-trophy 2019] Logika: přístupové údaje',
         'Přístupové údaje k webu https://logika.ntrophy.cz/ pro tým %s '
         'jsou:\n\n  * login: %s\n  * heslo: %s\n\nS pozdravem,\ntým logiky N-trophy' %
            (user.first_name, user.username, user.password),
         'logika@ntrophy.cz',
         [user.email])
        for user in users
    ]
    send_mass_mail(
        mails,
        fail_silently=False
    )

    return JsonResponse(
        {user.username: user.password for user in users}
    )
