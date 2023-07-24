from core.backups.databases.base import DBBackup
from core.connections.mysql import MySQLConnection

from logger import Logger

logger = Logger.get_logger()


class MySQLBackup(DBBackup):
    def __init__(self, connection: MySQLConnection):
        self.connection = connection

    def backup(self, backup_file_path: str, output_format: str) -> None:
        logger.info(">> Backing up MySQL database...")
