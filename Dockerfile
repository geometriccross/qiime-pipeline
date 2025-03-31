FROM mambaorg/micromamba

COPY env.yml /tmp/env.yml
RUN micromamba install -y -n base --file /tmp/env.yml && \
    micromamba clean --all --yes

