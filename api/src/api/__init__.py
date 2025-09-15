"""Entrypoint for the api package."""

import typer
import uvicorn
from fastapi import FastAPI
from loguru import logger

cli = typer.Typer()


class App:
    def __init__(self) -> None:
        self.app = FastAPI()

        from api.controllers import router

        self.app.include_router(router)

    @cli.command()
    def run(self, port: int = 8084, host: str = "0.0.0.0") -> None:
        logger.info("Starting API at http://{}:{}", host, port)
        uvicorn.run(self.app, host=host, port=port)
