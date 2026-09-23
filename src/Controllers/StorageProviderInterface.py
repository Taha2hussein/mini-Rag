from abc import ABC, abstractmethod


class StorageProviderInterface(ABC):
    """
    Interface عام لأي طريقة تخزين ملفات (ديسك محلي، S3، إلخ).
    أي كلاس هيطبّق التخزين لازم يلتزم بالـ methods دي بالظبط.
    """

    @abstractmethod
    def save_file(self, file, file_id: str) -> str:
        """
        بتحفظ الملف وترجّع الـ path أو الـ key اللي اتخزن بيه.
        """
        raise NotImplementedError

    @abstractmethod
    def get_file(self, file_id: str) -> bytes:
        """
        بترجّع محتوى الملف كـ bytes.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_file(self, file_id: str) -> bool:
        """
        بتمسح الملف، وترجّع True لو نجحت، False لو الملف مش موجود.
        """
        raise NotImplementedError

    @abstractmethod
    def file_exists(self, file_id: str) -> bool:
        """
        بتتأكد هل الملف موجود أصلاً قبل ما تحاولي تجيبيه أو تمسحيه.
        """
        raise NotImplementedError
    