# How to use different settings at different places


# ./manage.py migrate -settings=foo.settings.production
#or

# export DJANGO_SETTINGS_MODULE="foo.settings.jenkins"
#or

# gunicorn -w 4 -b 127.0.0.1:8001 -settings=foo.settings.dev
