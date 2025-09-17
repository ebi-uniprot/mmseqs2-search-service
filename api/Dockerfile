# Description: Dockerfile for the gentroutils package
#
# To run locally, you must have a credentials file for GCP. Assuming you do,
# you can run the following command:
#
# docker run -v /path/to/credentials.json:/app/credentials.json \
#     -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json  \
#     gentroutuls -s gwas_catalog_release
# By default the image uses the `config.yaml` file provided in the repository.
FROM python:3.13.7-slim-trixie

# Copy Rustc and Cargo from the rust-builder stage
# These are needed to install polars without compiling rust from source

# Copy Python source
COPY src /app/src
COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock
COPY README.md /app/README.md

ENV QUEUE_PASSWD=mypassword123 \
    QUEUE_USERNAME=user \
    QUEUE_HOST=rabbitmq \
    QUEUE_NAME=task_queue
# Build the executable
WORKDIR /app
RUN python -m pip install .

ENTRYPOINT ["api"]
