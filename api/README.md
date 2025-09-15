# mmseqs2 api

Installing the project

```{bash}
make dev
```

Building the docker image

```{bash}
make docker-build
```

Running the docker image

```{bash}
docker run -p 8084:8084 -v $(pwd)/tests/data:/static api:0.1.0
```

## Serving static files

Static files are served from the `/results` endpoint. The results are served from the `/static` directory in the container
