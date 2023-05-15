import argparse
from subprocess import CalledProcessError

from backups.mysql import MySQLBackup
from backups.postgres import PostgresBackup
from connections.mysql import MySQLConnection
from connections.postgres import PostgresConnection
from datetime import datetime
import configparser

from transfer.factory import FileSenderFactory

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-file', default='config.ini', required=False, help='Specify the config.ini file')
    parser.add_argument('--database', choices=['postgres', 'mysql', 'sqlite'], required=True,
                        help='Specify the database type')
    parser.add_argument('--output-format', choices=['sql', 'gz'], required=True, help='Specify the output format')
    parser.add_argument('--send-via', choices=['scp', 'boto3'], required=True, help='Specify the send method')
    parser.add_argument('--remove-after-sending', required=False,
                        help='Remove temp file after sending by scp or boto3')

    args = parser.parse_args()

    # Read the configuration file
    config = configparser.ConfigParser()
    config.read('config2.ini')

    # Select the database section based on the command-line argument
    database_section = args.database

    if database_section not in config.sections():
        raise ValueError(f'{database_section} section not found in config.')

    # Extract the configuration for the selected database
    db_config = dict(config[database_section])

    # Create a database connection object using the configuration
    if args.database == 'postgres':
        connection = PostgresConnection(db_config)
    elif args.database == 'mysql':
        connection = MySQLConnection(db_config)
    else:
        raise ValueError(f'Invalid database type: {args.database}')

    # Create a backup object for the selected database
    if args.database == 'postgres':
        backup = PostgresBackup(connection)
    elif args.database == 'mysql':
        backup = MySQLBackup(connection)
    else:
        raise ValueError(f'Invalid database type: {args.database}')

    # Specify the backup file path and output format
    output_format = args.output_format
    backup_file_path = f"./backup_{datetime.now():%a_%Y_%m_%d_%H%M%S}.{output_format}"

    # Perform the backup
    backup.backup(backup_file_path, output_format)

    # Send the backup file using the selected method
    sender_type = args.send_via

    if sender_type not in config.sections():
        raise ValueError(f'{sender_type} section not found in config.')

    sender_config = dict(config[sender_type])
    file_sender = FileSenderFactory.create_file_sender(sender_type, sender_config)
    try:
        file_sender.send_file(backup_file_path)
    except CalledProcessError:
        print("The file was not sent")

    remove_after_sending = True
    if args.remove_after_sending == "false":
        remove_after_sending = False

    if remove_after_sending:
        try:
            import os
            os.remove(backup_file_path)
            print(f"File '{backup_file_path}' deleted successfully.")
        except OSError as e:
            print(f"Error deleting file '{backup_file_path}': {e}")
