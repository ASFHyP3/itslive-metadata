FROM mambaorg/micromamba:2.3.0

LABEL org.opencontainers.image.title="HyP3 itslive-metadata"
LABEL org.opencontainers.image.description="ITS_LIVE granule metadata generator"
LABEL org.opencontainers.image.vendor="Alaska Satellite Facility"
LABEL org.opencontainers.image.authors="betolink <betolin@gmail.com>"
LABEL org.opencontainers.image.licenses="BSD-3-Clause"
LABEL org.opencontainers.image.url="https://github.com/betolink/itslive-metadata"
LABEL org.opencontainers.image.source="https://github.com/betolink/itslive-metadata"
LABEL org.opencontainers.image.documentation="https://hyp3-docs.asf.alaska.edu"

ENV MAMBA_DOCKERFILE_ACTIVATE=1 \
    MAMBA_CREATE_ENV=hyp3-itslive-metadata \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    SETUPTOOLS_SCM_PRETEND_VERSION=0.1.0

COPY --chown=$MAMBA_USER:$MAMBA_USER . /hyp3-itslive-metadata/

# Create and activate environment
RUN micromamba install -y -n base -f /hyp3-itslive-metadata/environment.yml && \
    micromamba clean --all --yes


ENTRYPOINT ["/usr/local/bin/_entrypoint.sh", "/hyp3-itslive-metadata/src/hyp3_itslive_metadata/etc/entrypoint.sh"]

