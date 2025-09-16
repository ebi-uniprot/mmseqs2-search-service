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

cli = typer.Typer()


class App:
    def __init__(self, fasta_output_path: str) -> None:
        """ASGI application."""
        self.fasta_output_path = self._verify_static_files_path(fasta_output_path)
        self.httpx_client = httpx.AsyncClient()
        self.app = FastAPI()
        self.app.mount("/results", StaticFiles(directory=self.fasta_output_path), name="static")

        self.app.include_router(router)

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
def run(port: int = 8084, host: str = "127.0.0.1", fasta_output_path="/static"):
    app = App(fasta_output_path=fasta_output_path)
    app.run(port=port, host=host)
