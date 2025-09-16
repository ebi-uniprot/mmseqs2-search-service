"""Fasta input model."""

import hashlib
import json
from functools import cached_property
from io import StringIO

from Bio import SeqIO
from pydantic import BaseModel, field_validator


class FastaBlobModel(BaseModel):
    """Model defining a fasta blob."""

    fasta: str

    @field_validator("fasta", mode="after")
    @classmethod
    def validate_fasta_string(cls, fasta_str: str) -> str:
        """Validate the fasta string by attempting to parse it and checking sequence content."""
        handle = StringIO(fasta_str)
        records = list(SeqIO.parse(handle, "fasta-pearson"))
        if not records:
            raise ValueError("No valid FASTA records found.")

        for record in records:
            seq = str(record.seq).upper()
            if not seq:
                raise ValueError("Found empty fasta sequence.")
            invalid = set(seq) - cls.allowed_characters()
            if invalid:
                raise ValueError("Found invalid fasta sequence.")
        return fasta_str

    @classmethod
    def allowed_characters(cls) -> set:
        """Return the set of allowed amino acid characters."""
        return set("ABCDEFGHIKLMNOPQRSTUVWXYZ*-X")

    @cached_property
    def job_id(self) -> str:
        """Generate a job id for the fasta content based on its contents."""
        h = hashlib.md5(self.fasta.encode("utf-8"))
        return h.hexdigest()

    def to_message(self) -> str:
        """Convert to the rabbit mq message."""
        return json.dumps({"job_id": self.job_id, "fasta": self.fasta})
