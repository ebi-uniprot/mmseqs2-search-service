"""Entrypoint for the api package."""

from __future__ import annotations

from collections.abc import MutableMapping
from pathlib import Path
from typing import Annotated, Any

import httpx
import typer
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger
from starlette.responses import Response as StarletteResponse

from api.controllers import router
from api.handlers.broker import BlockingQueueConnection
from api.handlers.db import MetaDataDb

cli = typer.Typer()


class CustomHeaderStaticFiles(StaticFiles):
    """Custom StaticFiles to add headers to responses.

    This class extends FastAPI's StaticFiles to include custom headers in the HTTP responses.

    This class is used to serve static files (like FASTA files) with specific headers, such as setting the
    Content-Type to "text/x-fasta" for FASTA files.
    """

    async def get_response(self, path: str, scope: MutableMapping[str, Any]) -> StarletteResponse:
        """Get response with custom headers.

        Args:
            path (str): The path to the static file.
            scope (MutableMapping[str, Any]): The ASGI scope.

        Returns:
            StarletteResponse: The response object with custom headers.
        """
        response = await super().get_response(path, scope)
        # Set a custom header, e.g., Content-Type
        if path.endswith(".fasta"):
            response.headers["content-type"] = "text/x-fasta"
        # Add other custom headers as needed
        return response


class App:
    def __init__(
        self,
        fasta_output_path: str,
        db_endpoint: str,
        db_port: int,
        queue_name: str,
        queue_username: str,
        queue_passwd: str,
        queue_port: int,
        queue_host: str,
    ) -> None:
        """ASGI application."""
        self.fasta_output_path = self._verify_static_files_path(fasta_output_path)
        self.httpx_client = httpx.AsyncClient()
        self.app = FastAPI()
        self.app.mount("/results", CustomHeaderStaticFiles(directory=self.fasta_output_path), name="static")

        # db
        self.db_endpoint = f"{db_endpoint.removesuffix(':')}:{db_port}"
        self.db = MetaDataDb(endpoint=self.db_endpoint, client=self.httpx_client)

        # queue
        self.queue_name = queue_name
        self.queue_username = queue_username
        self.queue_passwd = queue_passwd
        self.queue_port = queue_port
        self.queue_host = queue_host
        self.queue = BlockingQueueConnection(
            queue_name=self.queue_name,
            username=self.queue_username,
            passwd=self.queue_passwd,
            port=self.queue_port,
            host=self.queue_host,
        )

        # router
        self.app.include_router(router(self.db, self.queue))

    @staticmethod
    def _verify_static_files_path(p: str) -> Path:
        """Verify that the static files path exists and is a directory.

        Args:
            p (str): The path to verify.

        Returns:
            Path: The verified path as a Path object.

        Raises:
            AssertionError: If the path does not exist or is not a directory.

        """
        path = Path(p)
        assert path.is_dir(), f"Path {p} - path to the fasta outputs is not a directory."
        assert path.exists(), f"Path {p} - path to the fasta outputs does not exist or is not mounted."
        return path

    def run(self, port: int, host: str) -> None:
        """Run the ASGI application using Uvicorn.

        Args:
            port (int): The port to run the application on.
            host (str): The host to run the application on.
        """
        logger.info("Starting API at http://{}:{}", host, port)
        uvicorn.run(self.app, host=host, port=port)


@cli.command()
def run(
    app_port: Annotated[int, typer.Option(help="Port to run the application on", envvar="API_PORT")] = 8084,
    app_host: Annotated[str, typer.Option(help="Host to run the application on", envvar="API_HOST")] = "127.0.0.1",
    fasta_output_path: Annotated[
        str, typer.Option(help="Path to the FASTA output directory", envvar="API_FASTA_OUTPUT_PATH")
    ] = "/static",
    db_endpoint: Annotated[str, typer.Option(help="Database endpoint URL", envvar="DB_ENDPOINT")] = "127.0.0.1",
    db_port: Annotated[int, typer.Option(help="Database port", envvar="DB_PORT")] = 8085,
    queue_name: Annotated[str, typer.Option(help="Name of the message queue", envvar="QUEUE_NAME")] = "",
    queue_username: Annotated[str, typer.Option(help="Username for the message queue", envvar="QUEUE_USERNAME")] = "",
    queue_passwd: Annotated[str, typer.Option(help="Password for the message queue", envvar="QUEUE_PASSWD")] = "",
    queue_port: Annotated[int, typer.Option(help="Port for the message queue", envvar="QUEUE_PORT")] = 5672,
    queue_host: Annotated[str, typer.Option(help="Host for the message queue", envvar="QUEUE_HOST")] = "127.0.0.1",
):
    """CLI command to run the API application."""
    app = App(
        fasta_output_path=fasta_output_path,
        db_endpoint=db_endpoint,
        db_port=db_port,
        queue_name=queue_name,
        queue_username=queue_username,
        queue_passwd=queue_passwd,
        queue_port=queue_port,
        queue_host=queue_host,
    )
    app.run(port=app_port, host=app_host)
