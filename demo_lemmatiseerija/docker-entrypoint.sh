#!/bin/sh

export WORKERS=${WORKERS:-1}
export TIMEOUT=${TIMEOUT:-30}
export WORKER_CLASS=${WORKER_CLASS:-sync}

# siin ei ei ole tegelt gunicorni soovitatav kasutada

#exec /usr/bin/tini -- /usr/bin/gunicorn --bind=0.0.0.0:7000 \
#    "--workers=${WORKERS}" \
#    "--timeout=${TIMEOUT}" \
#    "--worker-class=${WORKER_CLASS}" \
#    --worker-tmp-dir=/dev/shm "$@" \
#    'demo_normaliseerija:demo()'

#exec /usr/bin/tini ./demo_lemmatiseerija.py
exec /usr/bin/python3 -u ./demo_lemmatiseerija.py