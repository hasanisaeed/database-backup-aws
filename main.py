from config.postgres import POSTGRES_CONFIG
from backups.postgres import PostgresBackup
from connections.postgres import PostgresConnection
from datetime import datetime
import configparser
from typing import Dict, Union

from transfer.factory import FileSenderFactory
from transfer.tools import FileSender

if __name__ == '__main__':
    # Create a PostgresConnection object using the configuration
    connection = PostgresConnection(**POSTGRES_CONFIG)

    # Create a PostgresBackup object
    postgres = PostgresBackup(connection)

    # Specify the backup file path and output format
    output_format = "gz"  # or sql
    backup_file_path = f"./backup_{datetime.now():%a_%Y_%m_%d_%H%M%S}.{output_format}"

    # Perform the backup
    postgres.backup(backup_file_path, output_format)

    sender_type: str = 'scp'  # or 'boto3'

    config = configparser.ConfigParser()
    config.read('config/transfer.ini')

    if sender_type not in config.sections():
        raise ValueError('Sender type not found in config.')

    sender_config: Dict[str, Union[str, int]] = dict(config[sender_type])
    file_sender: FileSender = FileSenderFactory.create_file_sender(sender_type, sender_config)
    file_sender.send_file(backup_file_path)
