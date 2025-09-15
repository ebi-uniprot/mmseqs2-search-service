"""Models for the API."""

import hashlib

from fastapi import File
from pydantic import BaseModel


class FileModel(BaseModel):
    file: bytes = File(description="A file read as bytes")

    @property
    def uuid(self) -> str:
        """Generate a UUID for the file based on its contents."""
        return hash_file(self.file)


def hash_file(file: bytes, algo="sha256") -> str:
    h = hashlib.new(algo)
    h.update(file)
    return h.hexdigest()
