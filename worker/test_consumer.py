
import json
import pytest
from unittest.mock import MagicMock, patch

import consumer
from consumer import *


@pytest.fixture
def mock_channel():
    return MagicMock()


@pytest.fixture
def sample_message():
    return {"job_id": 123, "payload": "hello"}


def test_handle_message_success(mock_channel, sample_message):
    body = json.dumps(sample_message).encode()

    with patch("consumer.mmseqs2_search", return_value={"status": "ok"}) as mock_mmseqs2_search, \
         patch("consumer.save_result") as mock_save:

        consumer.handle_message(mock_channel, MagicMock(), MagicMock(), body)

        # Verify processor was called
        mock_mmseqs2_search.assert_called_once_with(sample_message)

        # Verify db save was called
        mock_save.assert_called_once_with(sample_message["job_id"], {"status": "ok"})

        # Verify ack
        mock_channel.basic_ack.assert_called_once()


def test_handle_message_failure(mock_channel, sample_message):
    body = json.dumps(sample_message).encode()
    
    # Mock method with a delivery_tag
    mock_method = MagicMock()
    mock_method.delivery_tag = 42

    with patch("consumer.mmseqs2_search", side_effect=Exception("fail")), \
         patch("consumer.save_result") as mock_save:

        consumer.handle_message(mock_channel, mock_method, MagicMock(), body)

        # DB should not be called
        mock_save.assert_not_called()

        # basic_nack should be called with the correct delivery_tag
        mock_channel.basic_nack.assert_called_once_with(
            delivery_tag=42,
            requeue=False  # or True if your consumer requeues failed messages
        )