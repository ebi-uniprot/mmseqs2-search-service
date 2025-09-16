from unittest.mock import MagicMock, patch

from api.handlers.broker import BlockingQueueConnection


@patch("api.handlers.broker.pika.BlockingConnection")
def test_publish_message_success(mock_blocking_connection):
    mock_conn = MagicMock()
    mock_channel = MagicMock()
    mock_blocking_connection.return_value = mock_conn
    mock_conn.channel.return_value = mock_channel
    mock_conn.is_open = True

    broker = BlockingQueueConnection("queue", "user", "pass", 5672, "localhost")
    broker.publish_message('{"test": 1}')

    mock_blocking_connection.assert_called_once()
    mock_channel.queue_declare.assert_called_once_with(queue="queue", durable=True)
    mock_channel.confirm_delivery.assert_called_once()
    mock_channel.basic_publish.assert_called_once()
    mock_conn.close.assert_called_once()
