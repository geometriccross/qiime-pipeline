FROM mambaorg/micromamba

#https://micromamba-docker.readthedocs.io/en/latest/quick_start.html#running-commands-in-dockerfile-within-the-conda-environment
RUN micromamba install -y -n base qiime2-amplicon && \
    micromamba clean --all --yes

CMD ["/bin/bash"]
