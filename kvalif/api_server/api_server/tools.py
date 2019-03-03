from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.mail import send_mass_mail
from django.views.decorators.csrf import csrf_exempt

import json

@csrf_exempt
@login_required
@require_http_methods(['POST'])
@permission_required('add_user', 'change_user')
def user_create(request, *args, **kwargs):
    body = request.body.decode('utf-8')
    users = []
    for line in body.split('\n'):
        login, teamname, email = line.strip().split(',')


        u = User(
            username=login,
            first_name=teamname,
            email=email,
            is_active=True,
        )
        u.pwd=User.objects.make_random_password(),
        u.set_password(u.pwd[0])
        users.append(u)

    User.objects.bulk_create(users)

    mails = [
        ('[N-trophy 2019] Logika: přístupové údaje',
         'Přístupové údaje k webu https://logika.ntrophy.cz/ pro tým %s '
         'jsou:\n\n  * login: %s\n  * heslo: %s\n\nS pozdravem,\ntým logiky N-trophy' %
            (user.first_name, user.username, user.pwd[0]),
         'logika@ntrophy.cz',
         [user.email])
        for user in users
    ]
    send_mass_mail(
        mails,
        fail_silently=True
    )

    return JsonResponse(
        {user.username: user.pwd[0] for user in users}
    )
