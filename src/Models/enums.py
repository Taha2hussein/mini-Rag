from enum import Enum

class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    CSV = "csv"
    FILE_UPLOADED_SUCCESSFULLY = "File uploaded successfully"
    FILE_TYPE_NOT_ALLOWED = "File type not allowed"
    FILE_SIZE_NOT_ALLOWED = "File size exceeds limit"