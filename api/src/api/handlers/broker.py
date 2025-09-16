"""Handlers for broker-related operations."""

import pika
from loguru import logger
from pika.exceptions import UnroutableError

from api.status import TaskStatus


class BlockingQueueConnection:
    def __init__(
        self,
        queue_name: str,
        username: str,
        passwd: str,
        port: int = 5672,
        host: str = "mmseq2-rabbit-rabbitmq",
    ) -> None:
        self.port = port
        self.queue_name = queue_name
        self.username = username
        self.passwd = passwd
        self.host = host
        self.connection = None
        self.channel = None

    def __enter__(self):
        # Establish connection and channel when entering context
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=pika.PlainCredentials(
                    username=self.username,
                    password=self.passwd,
                ),
            )
        )
        logger.info("Connected to the broker")
        self.channel = self.connection.channel()
        # Ensure queue exists
        self.channel.queue_declare(queue=self.queue_name, durable=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up the connection when exiting the context
        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
                logger.info("Connection to the broker closed")
        except Exception as e:
            logger.error(f"Error closing broker connection: {e}")

    def publish_message(self, message: str) -> TaskStatus:
        """Publishes a JSON message (string) to the given RabbitMQ queue.

        Args:
            message (str): The message payload (already JSON string).
        """
        logger.debug("Passing the message")

        # Publish message
        if self.channel is None:
            raise ValueError("Establish connection to queue first.")
        self.channel.confirm_delivery()
        try:
            self.channel.basic_publish(
                exchange="",
                routing_key=self.queue_name,
                body=message.encode("utf-8"),  # ensure bytes
                properties=pika.BasicProperties(delivery_mode=2),  # persist message
            )
        except UnroutableError:
            return TaskStatus.FAILED

        logger.debug("Message Passed successfully")
        return TaskStatus.QUEUED
