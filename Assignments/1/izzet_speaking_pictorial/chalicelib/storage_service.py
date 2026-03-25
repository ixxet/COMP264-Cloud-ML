import boto3


class StorageService:
    def __init__(self, storage_location):
        self.client = boto3.client("s3")
        self.bucket_name = storage_location

    def get_storage_location(self):
        return self.bucket_name

    def upload_file(self, file_bytes, file_name, content_type=None):
        params = {
            "Bucket": self.bucket_name,
            "Body": file_bytes,
            "Key": file_name,
            "ACL": "public-read",
        }
        if content_type:
            params["ContentType"] = content_type

        self.client.put_object(**params)

        return {
            "fileId": file_name,
            "fileUrl": f"http://{self.bucket_name}.s3.amazonaws.com/{file_name}",
        }
