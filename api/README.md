# mmseqs2 api

A simple REST API for hosting the mmseqs2 service.

This API is the part of the service that is exposed to the user. It handles incoming requests, manages job submissions, and serves results.

## Develpment

To set up the project for development you can use the `Makefile` to create a virtual environment and install the dependencies.

> [!NOTE]
> The development is done with python 3.13 and uv as a dependency manager.

```{bash}
make dev # creates a virtual environment and installs dependencies, installs pre-commit hooks
```

### Running checks

Running checks on the codebase include:

- linting with `ruff`
- type checking with `mypy`
- formatting with `ruff`
- running tests with `pytest`
- checking for obsolete dependencies with `deptry`

Please make sure that the command below runs without errors before pushing your code.

```{bash}
make check
```

### Building the docker image

The docker image for the api can be built with the following command:

```{bash}
make docker-build
```

this builds the image for the current set up, the image is named `api` and tagged with the version in `pyproject.toml`.

### Running api in the docker image

Note that the api requires to have access to the `/static` directory where the mmseqs2 output files are stored. You can mount a local directory to the container with the `-v` option.

```{bash}
docker run -p 8084:8084 -v $(pwd)/tests/data:/static api:0.1.0
```

### Serving static files

By default, the API serves output files from the mmseqs2 runs on the `/results/:id` endpoint from the `/static` directory mounted to the container. You can change this by providing a different path to the app with `--fasta-output-path` when starting the app.

For instance the fasta static files can be mapped to the `/data` directory in the container like this:

```{bash}
docker run -p 8084:8084 -v $(pwd)/tests/data:/data api:0.1.0 --fasta-output-path /data
```

## Running API without docker

To run the API without docker, you need to have python 3.13 installed. You can then create a virtual environment and install the dependencies with:

```{bash}
uv run api
```

api will start the server on port 8084 by default. You can change the following options to the api command line:

| Option               | Type    | Description                                                                      | Env Var               | Default   |
| -------------------- | ------- | -------------------------------------------------------------------------------- | --------------------- | --------- |
| --app-port           | INTEGER | Port to run the application on                                                   | API_PORT              | 8084      |
| --app-host           | TEXT    | Host to run the application on                                                   | API_HOST              | 127.0.0.1 |
| --fasta-output-path  | TEXT    | Path to the FASTA output directory                                               | API_FASTA_OUTPUT_PATH | /static   |
| --db-endpoint        | TEXT    | Database endpoint URL                                                            | DB_ENDPOINT           | 127.0.0.1 |
| --db-port            | INTEGER | Database port                                                                    | DB_PORT               | 8085      |
| --queue-name         | TEXT    | Name of the message queue                                                        | QUEUE_NAME            |           |
| --queue-username     | TEXT    | Username for the message queue                                                   | QUEUE_USERNAME        |           |
| --queue-passwd       | TEXT    | Password for the message queue                                                   | QUEUE_PASSWD          |           |
| --queue-port         | INTEGER | Port for the message queue                                                       | QUEUE_PORT            | 5672      |
| --queue-host         | TEXT    | Host for the message queue                                                       | QUEUE_HOST            | 127.0.0.1 |
| --install-completion |         | Install completion for the current shell.                                        |                       |           |
| --show-completion    |         | Show completion for the current shell, to copy it or customize the installation. |                       |           |
| --help               |         | Show this message and exit.                                                      |                       |           |

## Design

The API is built with FastAPI and uses Pydantic models for data validation. It exposes three main endpoints:

- `POST /submit`: Accepts job submissions with a sequence in FASTA format and returns a job ID.
- `GET /status/{job_id}`: Returns the status of a job given its job ID.
- `GET /results/{job_id}`: Serves the results of a completed mmseqs2 job stored within the `/static` directory.

### Job Submission

When a job is submitted via the `POST /submit` endpoint, the API performs the following steps:

1. Validates the input data using Pydantic models.
2. Generates a unique job ID based on md5 hash of the input fasta string.
3. Performs the `GET:/job/{job_id}` request to the metadata service to find if the job is already present.
   4a. If the job is not present, it sends the job to the queue service (RabbitMQ) for processing and sends the `POST:/job` request to the metadata service to store the job metadata.
   4b. If the job is already present, it returns the existing job ID without re-submitting the job.

The response of the successful submission includes the `job_id` and `status` for the job.

### Job Status

After successful submission, the user can check the status of the job using the `GET /status/{job_id}` endpoint. The API will return the current status of the job, which can be one of the following:

- `QUEUED`: The job is waiting to be processed.
- `RUNNING`: The job is currently being processed.
- `FINISHED`: The job has finished processing, and the results are available.
- `FAILED`: The job has failed, and no results are available.

### Job Results

Once a job is completed, the user can retrieve the results using the `GET /results/{job_id}` endpoint. The API will return the results of the mmseqs2 job, which are stored in the `/static` directory.

### Error Handling

The API includes error handling for various scenarios, such as invalid input data, job not found, and internal server errors. Appropriate HTTP status codes and error messages are returned to the user in case of errors.

### OpenAPI Documentation

The OpenAPI documentation for the API is automatically generated by FastAPI and can be accessed at `/docs` when the server is running.
