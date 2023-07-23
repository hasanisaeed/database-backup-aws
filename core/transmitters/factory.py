from typing import Dict, Any

from core.transmitters.hub.aws import Boto3FileSender
from core.transmitters.hub.base import FileSender
from core.transmitters.hub.scp import ScpFileSender

from logger import LoggerSingleton

logger = LoggerSingleton.get_logger()


class FileSenderFactory:
    @staticmethod
    def create_file_sender(sender_type: str, config: Dict[str, Any]) -> FileSender:
        if sender_type == 'scp':
            return ScpFileSender(config)
        elif sender_type == 'boto3':
            return Boto3FileSender(config)
        else:
            logger.error('>> Invalid sender type.')
            raise ValueError('Invalid sender type.')
