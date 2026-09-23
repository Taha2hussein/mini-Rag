import boto3
from botocore.exceptions import ClientError
from .StorageProviderInterface import StorageProviderInterface



class S3StorageProvider(StorageProviderInterface):
    """
    تخزين الملفات على أي خدمة متوافقة مع S3 API
    (AWS S3, Filebase, Cloudflare R2, إلخ).
    """

    def __init__(
        self,
        bucket_name: str,
        access_key: str,
        secret_key: str,
        region: str = "us-east-1",
        endpoint_url: str = None,
    ):
        self.bucket_name = bucket_name
        self.client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            endpoint_url=endpoint_url,
        )

    def save_file(self, file, file_id: str) -> str:
        self.client.upload_fileobj(file.file, self.bucket_name, file_id)
        return f"{self.bucket_name}/{file_id}"

    def get_file(self, file_id: str) -> bytes:
        if not self.file_exists(file_id):
            raise FileNotFoundError(f"File {file_id} not found")
        response = self.client.get_object(Bucket=self.bucket_name, Key=file_id)
        return response["Body"].read()

    def delete_file(self, file_id: str) -> bool:
        if not self.file_exists(file_id):
            return False
        self.client.delete_object(Bucket=self.bucket_name, Key=file_id)
        return True

    def file_exists(self, file_id: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=file_id)
            return True
        except ClientError:
            return False