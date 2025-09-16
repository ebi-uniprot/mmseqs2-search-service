from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles

from api.models import FastaBlobModel

router = APIRouter(tags=["status"])
from httpx import Client
from loguru import logger
import pika

from typing import TypedDict

class StatusResponse(TypedDict):
    status: str
    uuid: str


@router.post("/submit")
async def submit(fasta_content: FastaBlobModel) -> dict:
    logger.debug("Received fasta content of size: {}", len(fasta_content))
    logger.debug("Fasta UUID: {}", fasta_content.uuid)
    logger.debug("Message: {}", fasta_content.to_message())
    publish_message("jobs", fasta_content.to_message()) 

    return {"status": "ok", "uuid": fasta_content.uuid}

def publish_message(queue_name: str, message: str, port: int = 5672):
    """
    Publishes a JSON message (string) to the given RabbitMQ queue.

    Args:
        queue_name (str): The queue to publish to.
        message (str): The message payload (already JSON string).
        port (int, optional): RabbitMQ port, defaults to 5672.
    """
    logger.debug("Passing the message")

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="mmseq2-rabbit-rabbitmq", port=5672, credentials=pika.PlainCredentials("user", "x1U4EJNzgQ1F4Fsl"))
    )
    print("Connected!")

    channel = connection.channel()

    # Ensure queue exists
    channel.queue_declare(queue=queue_name, durable=True)

    # Publish message
    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=message.encode("utf-8"),  # ensure bytes
        properties=pika.BasicProperties(delivery_mode=2)  # persist message
    )

    logger.debug("Message Passes")

    connection.close()
    return True


@router.get("/status/{uuid}")
async def status(uuid: str) -> StatusResponse:
    c = Client()
    response = c.get(f"http://example.com/status/{uuid}")
    return {"status": "ok", "uuid": uuid}


@router.get("/")
async def healthcheck():
    return {"status": "ok"}
