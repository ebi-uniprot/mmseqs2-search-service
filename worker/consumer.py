from pathlib import Path
import subprocess
import pika
import json
from queue_config import *
import tempfile

DB_PATH = Path("/app/swissprot")
WORKSPACE_DIR = Path("/workspace")
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)


def mmseqs2_search(job):
    """Run mmseqs easy-search on a FASTA sequence from the job."""
    job_id = job.get("job_id")
    if not job_id:
        # How will these ValueErrors be handled in the consumer?
        raise ValueError("Job must contain a job_id")

    fasta_content = job.get("fasta")
    if not fasta_content:
        raise ValueError("No FASTA content in job")

    with tempfile.TemporaryDirectory(dir=WORKSPACE_DIR) as tmpdirname:
        temp_dir = Path(tmpdirname)
        query_file = temp_dir / "input.fasta"

        # write FASTA to temp file
        with open(query_file, "w") as f:
            f.write(fasta_content)

        result_file = temp_dir / "results.m8"

        # This will be created and populated by mmseqs
        mmseqs_tmp_dir = temp_dir / "tmp"

        # build mmseqs easy-search command
        cmd = [
            "mmseqs",
            "easy-search",
            str(query_file),
            str(DB_PATH),
            str(result_file),
            str(mmseqs_tmp_dir),
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"mmseqs easy-search failed: {e.stderr.decode()}")
        return {"status": "processed"}


def save_result(job_id, result):
    # Replace this with your actual DB saving logic
    pass


def handle_message(ch, method, properties, body):
    """Callback for each RabbitMQ message."""
    try:
        job = json.loads(body)
        # step 1 search in mmseq2
        result = mmseqs2_search(job)
        # call the db api to save the result with status finished TODO
        # db.save_result(message["job_id"], result)
        save_result(job["job_id"], result)  # Placeholder actual implementation
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print("Failed to process job:", e)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start_consumer():
    """Start RabbitMQ consumer and listen for messages."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    # Ensure queue exists
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=handle_message)
    print("Waiting for jobs. To exit press CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Interrupted")
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    start_consumer()
