import pika
import json
from queue_config import *

def mmseqs2_search(body):
    # Replace this with your actual job processing logic
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
        save_result(job["job_id"], result) # Placeholder actual implementation
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
    print('Waiting for jobs. To exit press CTRL+C')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print('Interrupted')
        channel.stop_consuming()
    finally:
        connection.close()

if __name__ == '__main__':
    start_consumer()