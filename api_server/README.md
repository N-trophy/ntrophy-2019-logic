# N-trophy 2019 logic qualification task

## How to run server for development

```
$ cp api_server/settings/local.py.txt api_server/settings/local.py
Edit api_server/settings/local.py as you wish.
$ virtualenv -p python3 djangoenv
$ source djangoenv/bin/activate
$ pip3 install -r requirements.txt
$ ./manage.py command --settings=api_server.settings.local
$ ./manage.py runserver --settings=api_server.settings.local
```

## How to deploy to production

```
$ cp api_server/settings/production.py.txt api_server/settings/production.py
Edit api_server/settings/local.py as you wish.
$ ./manage.py collectstatic --settings=api_server.settings.production
```
