import argparse

from datetime import datetime
from subprocess import CalledProcessError
import json

from core.connections.mysql import MySQLConnection
from core.connections.postgres import PostgresConnection
from core.backups.databases.mysql import MySQLBackup
from core.backups.databases.postgres import PostgresBackup
from core.exceptions.transmitters import SendingFileErrorException
from core.transmitters.factory import FileSenderFactory


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-file', default='config.ini', required=False, help='Specify the config.ini file')
    parser.add_argument('--output-format', choices=['sql', 'gz'], required=True, help='Specify the output format')
    parser.add_argument('--send-via', choices=['scp', 'boto3'], required=True, help='Specify the send method')
    parser.add_argument('--interval', default="12h", required=False, help='Interval')
    parser.add_argument('--remove-after-sending', default="true", required=False,
                        help='Remove temp file after sending by scp or boto3')

    return parser.parse_args()


def read_config(config_file):
    with open(config_file, 'r') as file:
        config_data = json.load(file)
    return config_data


def get_connection(database, db_config):
    if database == 'postgres':
        return PostgresConnection(db_config)
    elif database == 'mysql':
        return MySQLConnection(db_config)
    else:
        raise ValueError(f'Invalid database type: {database}')


def get_backup(database, connection):
    if database == 'postgres':
        return PostgresBackup(connection)
    elif database == 'mysql':
        return MySQLBackup(connection)
    else:
        raise ValueError(f'Invalid database type: {database}')


def perform_backup(backup, backup_file_path, output_format):
    backup.backup(backup_file_path, output_format)


def send_backup(file_sender, backup_file_path):
    try:
        file_sender.send_file(backup_file_path)
    except CalledProcessError:
        raise SendingFileErrorException(f"The file {backup_file_path} was not sent!")


def remove_backup_file(backup_file_path):
    try:
        import os
        os.remove(backup_file_path)
        print(f">> Temp file '{backup_file_path}' deleted successfully.")
    except OSError as e:
        print(f">> Error deleting file '{backup_file_path}': {e}")


def main():
    args = parse_arguments()
    config = read_config(args.config_file)
    sender_type = args.send_via
    databases = config['databases']

    for db_config in databases:

        connection = get_connection(db_config.get('type'), db_config)

        backup = get_backup(args.database, connection)

        output_format = args.output_format
        backup_file_path = f"./backup_{datetime.now():%a_%Y_%m_%d_%H%M%S}.{output_format}"

        perform_backup(backup, backup_file_path, output_format)

        if sender_type not in config.get('transmitters'):
            raise ValueError(f'{sender_type} section not found in config.')

        sender_config = config.get('transmitters')[sender_type]
        file_sender = FileSenderFactory.create_file_sender(sender_type, sender_config)

        send_backup(file_sender, backup_file_path)

        remove_after_sending = args.remove_after_sending.lower() == "true"

        if remove_after_sending:
            remove_backup_file(backup_file_path)


if __name__ == '__main__':
    main()
