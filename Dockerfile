
# TODO: Skal fikse permissions til at write + skift workdir fordi matplotlib brokker sig
FROM mambaorg/micromamba:latest

USER root
RUN apt-get -y update && apt-get install -y chromium chromium-driver && apt-get -y autoremove && apt-get -y autoclean

USER $MAMBA_USER
COPY --chown=$MAMBA_USER:$MAMBA_USER env.yaml /tmp/env.yaml
RUN micromamba install -y -f /tmp/env.yaml && \
    micromamba clean --all --yes

WORKDIR /scraper

