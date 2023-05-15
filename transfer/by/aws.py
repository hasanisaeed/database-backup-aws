import boto3

from transfer.by.base import FileSender


class Boto3FileSender(FileSender):
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str) -> None:
        self.aws_access_key_id: str = aws_access_key_id
        self.aws_secret_access_key: str = aws_secret_access_key

    def send_file(self, file_path: str) -> None:
        session: boto3.Session = boto3.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )
        s3_client: boto3.client = session.client('s3')
        s3_client.upload_file(file_path, 'your-bucket-name', 'destination-file-name')
