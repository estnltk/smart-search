#!/bin/sh

# siin ei ei ole tegelt gunicorni soovitatav kasutada
#
#export WORKERS=${WORKERS:-1}
#export TIMEOUT=${TIMEOUT:-30}
#export WORKER_CLASS=${WORKER_CLASS:-sync}
#exec /usr/bin/tini -- /usr/bin/gunicorn --bind=0.0.0.0:7000 \
#    "--workers=${WORKERS}" \
#    "--timeout=${TIMEOUT}" \
#    "--worker-class=${WORKER_CLASS}" \
#    --worker-tmp-dir=/dev/shm "$@" \
#    'demo_normaliseerija:demo()'

exec /usr/bin/tini ./demo_smartsearch_veebileht.py