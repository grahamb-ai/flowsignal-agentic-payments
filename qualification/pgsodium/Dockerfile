# FS-SZ-PAY-001 pgsodium compatibility experiment (isolated)

FROM postgres:16-bookworm
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl build-essential libsodium-dev postgresql-server-dev-16 \
 && rm -rf /var/lib/apt/lists/*
ARG PGSODIUM_VERSION=3.1.8
RUN curl --fail --location --retry 3 "https://api.pgxn.org/dist/pgsodium/${PGSODIUM_VERSION}/pgsodium-${PGSODIUM_VERSION}.zip" -o /tmp/pgsodium.zip \
 && apt-get update && apt-get install -y --no-install-recommends unzip \
 && mkdir /tmp/pgsodium-src && cd /tmp/pgsodium-src \
 && unzip -q /tmp/pgsodium.zip \
 && cd pgsodium-${PGSODIUM_VERSION} \
 && make USE_PGXS=1 && make USE_PGXS=1 install \
 && rm -rf /tmp/pgsodium-src /tmp/pgsodium.zip /var/lib/apt/lists/*
# EVALUATION ONLY: fetched archive must be digest-pinned and source-reviewed
# before this image or its output can count as a qualified security component.
