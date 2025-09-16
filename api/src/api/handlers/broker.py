"""Handlers for broker-related operations."""

import pika
from fastapi import HTTPException
from pika.exceptions import UnroutableError


class BlockingQueueConnection:
    """Blocking connection to RabbitMQ queue."""

    def __init__(
        self,
        queue_name: str,
        username: str,
        passwd: str,
        port: int,
        host: str,
    ) -> None:
        """Initialize the connection parameters.

        Args:
            queue_name (str): The name of the RabbitMQ queue.
            username (str): The username for RabbitMQ authentication.
            passwd (str): The password for RabbitMQ authentication.
            port (int): The port number for RabbitMQ connection.
            host (str): The hostname or IP address of the RabbitMQ server.

        """
        self.port = port
        self.queue_name = queue_name
        self.username = username
        self.passwd = passwd
        self.host = host

    def publish_message(self, message: str) -> None:
        """Publishes a JSON message (string) to the given RabbitMQ queue.

        This method :
        * establishes a blocking connection to the RabbitMQ server,
        * declares the queue (idempotent operation),
        * publishes the message with delivery confirmation,
        * closes the connection.

        In the case of failure to route the message, an HTTPException with status code 400 is raised.

        Args:
            message (str): The message payload (already JSON string).

        Raises:
            HTTPException: If the message could not be routed to the queue.
        """
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    credentials=pika.PlainCredentials(
                        username=self.username,
                        password=self.passwd,
                    ),
                )
            )
            channel = connection.channel()
            channel.queue_declare(queue=self.queue_name, durable=True)

            channel.confirm_delivery()
            channel.basic_publish(
                exchange="",
                routing_key=self.queue_name,
                body=message.encode("utf-8"),  # ensure bytes
                properties=pika.BasicProperties(delivery_mode=2),  # persist message
            )
        except UnroutableError:
            raise HTTPException(status_code=400, detail="Failed to upload task to the queue")

        if connection and connection.is_open:
            connection.close()
