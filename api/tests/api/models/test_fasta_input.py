"""Test fasta input model."""

import json
from pathlib import Path

import pytest

from api.models.fasta_input import FastaBlobModel


def test_fasta_input_from_mock(mocks: Path) -> None:
    """Construct FastaInput from mock file and attempt to validate it."""
    mock_file = mocks / "user_submit_job_to_api.json"
    assert mock_file.exists(), f"Mock file does not exist: {mock_file}"
    assert mock_file.is_file(), f"Mock file is not a file: {mock_file}"
    with open(mock_file) as f:
        data = json.load(f)
    assert "fasta" in data, "Mock file does not contain 'fasta' key"

    fasta_input = FastaBlobModel(**data)
    assert isinstance(fasta_input, FastaBlobModel)

    assert fasta_input.to_message() == json.dumps({"job_id": fasta_input.job_id, "fasta": fasta_input.fasta})


def test_fasta_input_with_multiple_sequences(static_files: Path) -> None:
    """Test fasta input with multiple sequences."""
    fasta_file = static_files / "sequence.fasta"
    assert fasta_file.exists(), f"Fasta file does not exist: {fasta_file}"
    assert fasta_file.is_file(), f"Fasta file is not a file: {fasta_file}"
    fasta_data = fasta_file.read_text()
    fasta_input = FastaBlobModel(fasta=fasta_data)
    assert isinstance(fasta_input, FastaBlobModel)


@pytest.mark.parametrize(
    ("invalid_fasta", "error_msg"),
    [
        pytest.param("", "No valid FASTA records found.", id="empty string"),
        pytest.param("This is not a valid FASTA format", "No valid FASTA records found.", id="random text"),
        pytest.param(">seq1\nMPQ\n>seq2\nINQ!!!", "Found invalid fasta sequence.", id="invalid sequence characters"),
        pytest.param(">seq1\nMKTA\n>seq2\n", "Found empty fasta sequence.", id="missing sequence"),
    ],
)
def test_invalid_fasta_input(invalid_fasta: str, error_msg: str) -> None:
    """Test invalid fasta input."""
    with pytest.raises(ValueError) as exc_info:
        FastaBlobModel(fasta=invalid_fasta)
    assert error_msg in str(exc_info.value)
