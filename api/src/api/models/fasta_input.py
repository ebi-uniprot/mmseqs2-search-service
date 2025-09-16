"""Fasta input model."""

import hashlib
import json
from functools import cached_property
from io import StringIO

from Bio import SeqIO
from pydantic import BaseModel, ValidationError, field_validator


class FastaBlobModel(BaseModel):
    """Model defining a fasta blob."""

    fasta: str

    @field_validator("fasta_content", mode="after")
    @classmethod
    def validate_fasta_string(cls, fasta_str: str) -> str:
        """Validate the fasta string by attempting to parse it."""
        try:
            handle = StringIO(fasta_str)
            records = list(SeqIO.parse(handle, "fasta"))
        except Exception as e:
            raise ValidationError(f"Error parsing FASTA content: {e}")
        if not records:
            raise ValidationError("No valid FASTA records found.")
        return fasta_str

    @cached_property
    def job_id(self) -> str:
        """Generate a job id for the fasta content based on its contents."""
        h = hashlib.md5(self.fasta.encode("utf-8"))
        return h.hexdigest()

    def __len__(self) -> int:
        """Get the number of lines in the fasta content."""
        return self.fasta.count("\n")

    def to_message(self) -> str:
        """Convert to the rabbit mq message."""
        return json.dumps({"job_id": self.job_id, "fasta_content": self.fasta})
