 # demo veebileht
 
 FROM ubuntu

# install python requests and other stuff
RUN apt-get update && apt-get install -y \
    tini \
    gunicorn \
    python3-requests \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# create an unprivileged user
RUN addgroup --gid 1001 "mere_mortal" \
    && adduser --disabled-password --gecos "mere_mortal user,,," --home /home4mere_mortal --ingroup mere_mortal --uid 1001 mere_mortal

# everything from here down runs as the unprivileged user account 
USER mere_mortal:mere_mortal
WORKDIR /home4mere_mortal

# copy current task related skripts
COPY --chown=mere_mortal:mere_mortal docker-entrypoint.sh  demo_lemmatiseerija.py ./
RUN chmod +x docker-entrypoint.sh demo_lemmatiseerija.py

# parameters for gunicorn
ENV WORKERS=1
ENV TIMEOUT=30
ENV WORKER_CLASS=sync
ENV LOGURU_LEVEL=INFO

# start web server
#ENTRYPOINT ["./docker-entrypoint.sh"]
ENTRYPOINT ["/usr/bin/tini", "--", "./docker-entrypoint.sh"]
