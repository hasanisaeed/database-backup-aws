from typing import Dict

import boto3
from boto3.exceptions import S3UploadFailedError

from core.transmitters.hub.base import FileSender

from logger import LoggerSingleton

logger = LoggerSingleton.get_logger()


class Boto3FileSender(FileSender):
    def __init__(self, config: Dict[str, str]) -> None:
        self.aws_access_key_id: str = config['aws_access_key_id']
        self.aws_secret_access_key: str = config['aws_secret_access_key']
        self.aws_bucket_name: str = config['aws_bucket_name']
        self.aws_destination_file_name: str = config['aws_destination_file_name']

    def send_file(self, file_path: str) -> None:
        session: boto3.Session = boto3.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )
        s3_client: boto3.client = session.client('s3')
        try:
            s3_client.upload_file(file_path, self.aws_bucket_name, self.aws_destination_file_name)
        except S3UploadFailedError:
            logger.error(">> Boto3 sending file error")
