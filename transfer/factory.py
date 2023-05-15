from typing import Dict, Any

from transfer.aws import Boto3FileSender
from transfer.base import FileSender
from transfer.scp import ScpFileSender


class FileSenderFactory:
    @staticmethod
    def create_file_sender(sender_type: str, **kwargs: Dict[str, Any]) -> FileSender:
        if sender_type == 'scp':
            return ScpFileSender(**kwargs)
        elif sender_type == 'boto3':
            return Boto3FileSender(**kwargs)
        else:
            raise ValueError('Invalid sender type.')
