"""Models for the API."""

import hashlib
from functools import cached_property

from pydantic import BaseModel


class FastaBlobModel(BaseModel):
    fasta_content: str

    @cached_property
    def uuid(self) -> str:
        """Generate a UUID for the fasta content based on its contents."""
        h = hashlib.new("sha256")
        h.update(self.fasta_content.encode("utf-8"))
        return h.hexdigest()

    def __len__(self) -> int:
        """Get the number of lines in the fasta content."""
        return self.fasta_content.count("\n")

    def to_message(self) -> dict:
        """Convert to the rabbit mq message."""
        return {"uuid": self.uuid, "fasta_content": self.fasta_content}
