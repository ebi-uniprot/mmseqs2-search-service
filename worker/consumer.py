import pika
import json
from queue_config import *
import logging
import sys
import requests
import os
from mmseqs_service import MMSeqsService

# Rabbit related configuration with environment variable overrides
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", RABBITMQ_PORT))
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", RABBITMQ_HOST)
QUEUE_NAME = os.getenv("QUEUE_NAME", QUEUE_NAME)
USER_NAME = os.getenv("USER_NAME", USER_NAME)
PASSWORD = os.getenv("PASSWORD", PASSWORD)  

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stdout,
)

DB_DIR = "/app/mmseqs_db/swissprot"
WORKSPACE_DIR = "/workspace"
RESULT_DIR = "/results"
DB_API_BASE_URL = "http://meta-database:8000"


mmseqsService =  MMSeqsService(DB_DIR, WORKSPACE_DIR, RESULT_DIR)


def update_job_status(job_id, job_status):
    """Update job status in the database via API call."""
    pass
    # api_url = f"{DB_API_BASE_URL}/{job_id}"
    # payload = {"status": job_status}
    # try:
    #     response = requests.patch(api_url, json=payload)
    #     response.raise_for_status() # raises error if status_code >= 400
    #     logging.info(f"Updated job {job_id} status to {job_status}")
    # except requests.RequestException as e:
    #     logging.error(f"Failed to update job status for {job_id}: {e}")
    #     raise Exception(f"Failed to update job status for {job_id}: {e}")


def handle_message(ch, method, properties, body):
    """Callback for each RabbitMQ message."""
    try:
        job = json.loads(body)
        # step 1 set the status to Running
        logging.info(f"Received job: {job}")
        update_job_status(job["job_id"], "Running")
        # step 2 search in mmseq2
        mmseqsService.mmseqs2_search(job)
        # step 3 call the db api to save the result with status finished
        update_job_status(job["job_id"], "Finished")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logging.error("Failed to process job: %s", e, exc_info=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start_consumer():
    """Start RabbitMQ consumer and listen for messages."""
    credentials = pika.PlainCredentials(USER_NAME, PASSWORD)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)
    )
    channel = connection.channel()
    # Ensure queue exists
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=handle_message)
    logging.info("Waiting for jobs. To exit press CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logging.info("Interrupted")
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    start_consumer()
