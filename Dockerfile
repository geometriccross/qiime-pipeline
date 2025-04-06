FROM mambaorg/micromamba

#https://micromamba-docker.readthedocs.io/en/latest/quick_start.html#running-commands-in-dockerfile-within-the-conda-environment
COPY env.yml /tmp/env.yml
RUN micromamba install -y -n base --file /tmp/env.yml && \
    micromamba clean --all --yes

COPY scripts /scripts

CMD ["/bin/bash"]
