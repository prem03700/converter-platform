import os

from app.config import settings
from app.storage.base import StorageBackend
from app.utils.validation import FileValidationError


class LocalStorage(StorageBackend):
    def __init__(self, root: str | None = None):
        self.root = os.path.abspath(root or settings.LOCAL_STORAGE_PATH)
        os.makedirs(self.root, exist_ok=True)

    def _resolve(self, key: str) -> str:
        # Prevent path traversal: resolved path must stay inside self.root.
        path = os.path.abspath(os.path.join(self.root, key))
        if not path.startswith(self.root + os.sep) and path != self.root:
            raise FileValidationError("Invalid storage key")
        return path

    def save(self, key: str, data: bytes) -> str:
        path = self._resolve(key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        return key

    def read(self, key: str) -> bytes:
        path = self._resolve(key)
        with open(path, "rb") as f:
            return f.read()

    def delete(self, key: str) -> None:
        path = self._resolve(key)
        if os.path.exists(path):
            os.remove(path)

    def url_for(self, key: str, expires_in: int = 3600) -> str:
        # In local dev, files are served via the /api/v1/files/{id}/download
        # endpoint rather than a direct static URL.
        return f"/api/v1/download/{key}"
