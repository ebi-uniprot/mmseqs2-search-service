# Description: Dockerfile for the gentroutils package
#
# To run locally, you must have a credentials file for GCP. Assuming you do,
# you can run the following command:
#
# docker run -v /path/to/credentials.json:/app/credentials.json \
#     -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json  \
#     gentroutuls -s gwas_catalog_release
# By default the image uses the `config.yaml` file provided in the repository.
FROM rust:slim-trixie AS rust-builder
FROM python:3.13.7-slim-trixie

# Copy Rustc and Cargo from the rust-builder stage
# These are needed to install polars without compiling rust from source
COPY --from=rust-builder /usr/local/cargo/bin/rustc /usr/local/bin/rustc
COPY --from=rust-builder /usr/local/cargo/bin/cargo /usr/local/bin/cargo

# Copy Python source
COPY src /app/src
COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock
COPY README.md /app/README.md

# Build the executable
WORKDIR /app
RUN python -m pip install .

ENTRYPOINT [ "api"]
