FROM ghcr.io/prefix-dev/pixi:0.68.1

LABEL org.opencontainers.image.source="https://github.com/annefou/marine-heatwave-replication"
LABEL org.opencontainers.image.description="Replication study container for marine-heatwave-replication"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

# git is required to install the environment, not merely convenient: XMHW — the
# independent MHW detection engine, and the reason this is a Replication rather
# than a Reproduction — is not on conda-forge or PyPI, so pixi.toml pins it to a
# git revision and `pixi install` shells out to git to fetch it. The
# prefix-dev/pixi base image ships without git, so the build fails with
# "Git executable not found" at the install step.
#
# No USER switching: this image's config declares User "" and PATH
# /root/.pixi/bin, i.e. it already runs as root (checked against the registry,
# not assumed — an earlier version of this file switched to $MAMBA_USER, which
# does not exist here and would have failed the build).
RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install the pinned environment first (separate from source copy so the lock
# layer is cached across source-only edits).
COPY pixi.toml pixi.lock /app/
RUN pixi install --locked

COPY . /app

# Mount credentials at runtime, or pass them as environment variables. This
# image runs as root, so paths are under /root — the previous example pointed at
# /home/mambauser, which does not exist here.
#
#   docker run -e COPERNICUSMARINE_SERVICE_USERNAME -e COPERNICUSMARINE_SERVICE_PASSWORD \
#     ghcr.io/annefou/marine-heatwave-replication:latest
#
# or with the credentials file:
#   docker run -v ~/.copernicusmarine:/root/.copernicusmarine \
#     ghcr.io/annefou/marine-heatwave-replication:latest
#
# See data/README.md for what each input needs.

CMD ["pixi", "run", "snakemake", "--cores", "1"]
