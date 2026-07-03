"""
Common storage interface so the rest of the app never knows whether
files live on local disk (development) or in S3 (production). Swapping
backends is just a config change (STORAGE_BACKEND=local|s3).
"""
from abc import ABC, abstractmethod


class StorageBackend(ABC):
    @abstractmethod
    def save(self, key: str, data: bytes) -> str:
        """Persists data under `key`, returns the storage key actually used."""

    @abstractmethod
    def read(self, key: str) -> bytes:
        """Returns the raw bytes stored under `key`."""

    @abstractmethod
    def delete(self, key: str) -> None:
        ...

    @abstractmethod
    def url_for(self, key: str, expires_in: int = 3600) -> str:
        """Returns a (possibly signed/temporary) URL for downloading the file."""
