#! /bin/sh
ps auxww | grep celery | grep -v 'grep' | awk '{print $2}' | xargs kill -HUP

