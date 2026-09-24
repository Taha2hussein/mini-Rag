# Controllers/LocalStorageProvider.py

import os
from pathlib import Path

from .StorageProviderInterface import StorageProviderInterface


class LocalStorageProvider(StorageProviderInterface):
    """
    تخزين الملفات على الديسك المحلي للسيرفر.
    مناسب للتعلم والتطوير، مش لإنتاج فيه يوزرز كتير.
    """

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_path(self, file_id: str) -> str:
        return os.path.join(self.base_dir, file_id)

    def save_file(self, file, file_id: str) -> str:
        file_path = self._get_path(file_id)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)   # ← السطر الجديد
        with open(file_path, "wb") as f:
           f.write(file.file.read())
        return file_path

    def get_file(self, file_id: str) -> bytes:
        file_path = self._get_path(file_id)
        if not self.file_exists(file_id):
            raise FileNotFoundError(f"File {file_id} not found")
        with open(file_path, "rb") as f:
            return f.read()

    def delete_file(self, file_id: str) -> bool:
        file_path = self._get_path(file_id)
        if not self.file_exists(file_id):
            return False
        os.remove(file_path)
        return True

    def file_exists(self, file_id: str) -> bool:
        return Path(self._get_path(file_id)).is_file()