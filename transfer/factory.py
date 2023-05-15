from typing import Dict, Any

from transfer.by import FileSender
from transfer.by.aws import Boto3FileSender
from transfer.by.scp import ScpFileSender


class FileSenderFactory:
    @staticmethod
    def create_file_sender(sender_type: str, config: Dict[str, Any]) -> FileSender:
        if sender_type == 'scp':
            return ScpFileSender(config)
        elif sender_type == 'boto3':
            return Boto3FileSender(config)
        else:
            raise ValueError('Invalid sender type.')
