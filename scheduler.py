import argparse
import os
import json
import sched
import time
from datetime import datetime
from subprocess import CalledProcessError

from core.connections.mysql import MySQLConnection
from core.connections.postgres import PostgresConnection
from core.backups.databases.mysql import MySQLBackup
from core.backups.databases.postgres import PostgresBackup
from core.transmitters.factory import FileSenderFactory

from logger import Logger
from utils import convert_to_seconds

logger = Logger.get_logger()
PRIORITY = 1


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-file', default='config.json', required=False, help='Specify the config.ini file')
    parser.add_argument('--output-format', choices=['sql', 'gz'], required=True, help='Specify the output format')
    parser.add_argument('--backup-folder', default='./backups', required=False, help='Default backup folder')
    parser.add_argument('--send-via', choices=['scp', 'boto3'], required=True, help='Specify the send method')
    parser.add_argument('--interval', default="12h", required=False, help='Interval')
    parser.add_argument('--remove-after-sending', default="false", required=False,
                        help='Remove temp file after sending by transmitter')
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
        logger.error(f'Invalid database type: {database}')


def get_backup(database, connection):
    if database == 'postgres':
        return PostgresBackup(connection)
    elif database == 'mysql':
        return MySQLBackup(connection)
    else:
        logger.error(f'Invalid database type: {database}')


def perform_backup(backup, backup_file_path, output_format):
    return backup.backup(backup_file_path, output_format)


def send_backup(file_sender, backup_file_path):
    try:
        file_sender.send_file(backup_file_path)
    except CalledProcessError:
        logger.error(f'The file {backup_file_path} was not sent!')


def remove_backup_file(backup_file_path):
    try:
        os.remove(backup_file_path)
        logger.info(f">> Temp file '{backup_file_path}' deleted successfully.")
    except OSError as e:
        logger.error(f">> Error deleting file '{backup_file_path}': {e}")


def main():
    args = parse_arguments()
    config = read_config(args.config_file)
    databases = config['databases']

    for db_config in databases:
        database_type = db_config.get('type')
        connection = get_connection(database_type, db_config)
        backup = get_backup(database_type, connection)
        output_format = args.output_format
        backup_folder = args.backup_folder

        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        backup_file_path = os.path.join(backup_folder,
                                        f"{db_config.get('database')}_{datetime.now():%a_%Y_%m_%d_%H%M%S}.{output_format}")
        backup_is_success = perform_backup(backup, backup_file_path, output_format)

        if backup_is_success:
            sender_type = args.send_via
            sender_config = config.get('transmitters')[sender_type]
            file_sender = FileSenderFactory.create_file_sender(sender_type, sender_config)
            send_backup(file_sender, backup_file_path)

            remove_after_sending = args.remove_after_sending.lower() == "true"
            if remove_after_sending:
                remove_backup_file(backup_file_path)

    logger.info(f"Backup and send process completed for {db_config.get('database')}.")


def run_and_reschedule(scheduler, delay):
    try:
        main()
    except Exception as e:
        logger.error(f"An error occurred during the main execution: {e}")
    finally:
        scheduler.enter(delay, PRIORITY, run_and_reschedule, (scheduler, delay))
        logger.info(f"Next run scheduled in {delay} seconds.")


def start_scheduler():
    args = parse_arguments()
    s = sched.scheduler(time.time, time.sleep)

    interval = args.interval
    delay = convert_to_seconds(interval)

    logger.info("Scheduler starting. First run will be immediate.")
    s.enter(0, PRIORITY, run_and_reschedule, (s, delay))
    s.run()


if __name__ == '__main__':
    start_scheduler()