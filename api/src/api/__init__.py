"""Entrypoint for the api package."""

from __future__ import annotations

from pathlib import Path

import httpx
import typer
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger

from api.controllers import router
from api.handlers.broker import BlockingQueueConnection
from api.handlers.db import MetaDataDb

cli = typer.Typer()


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
        self.app.mount("/results", StaticFiles(directory=self.fasta_output_path), name="static")

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
        self.app.include_router(router(self.db, self.queue))

    @staticmethod
    def _verify_static_files_path(p: str) -> Path:
        path = Path(p)
        assert path.is_dir(), f"Path {p} - path to the fasta outputs is not a directory."
        assert path.exists(), f"Path {p} - path to the fasta outputs does not exist or is not mounted."
        return path

    def run(self, port: int, host: str) -> None:
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
