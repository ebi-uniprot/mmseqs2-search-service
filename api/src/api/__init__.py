"""Entrypoint for the api package."""

from __future__ import annotations

from collections.abc import MutableMapping
from pathlib import Path
from typing import Any

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
        self.db_endpoint = db_endpoint
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
    app_port: int = 8084,
    app_host: str = "127.0.0.1",
    fasta_output_path="/static",
    db_endpoint: str = "",
    queue_name: str = "",
    queue_username: str = "",
    queue_passwd: str = "",
    queue_port: int = 5672,
    queue_host: str = "127.0.0.1",
):
    """CLI command to run the API application.

    Args:
        app_port (int): The port to run the application on. Default is 8084.
        app_host (str): The host to run the application on. Default is "127.0.0.1".
        fasta_output_path (str): The path to the FASTA output directory. Default is "/static".
        db_endpoint (str): The database endpoint URL. Default is "".
        queue_name (str): The name of the message queue. Default is "".
        queue_username (str): The username for the message queue. Default is "".
        queue_passwd (str): The password for the message queue. Default is "".
        queue_port (int): The port for the message queue. Default is 5672.
        queue_host (str): The host for the message queue. Default is "127.0.0.1".

    """
    app = App(
        fasta_output_path=fasta_output_path,
        db_endpoint=db_endpoint,
        queue_name=queue_name,
        queue_username=queue_username,
        queue_passwd=queue_passwd,
        queue_port=queue_port,
        queue_host=queue_host,
    )
    app.run(port=app_port, host=app_host)
