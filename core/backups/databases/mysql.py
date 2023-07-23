from core.backups.databases.base import DBBackup
from core.connections.mysql import MySQLConnection


class MySQLBackup(DBBackup):
    def __init__(self, connection: MySQLConnection):
        self.connection = connection

    def backup(self, backup_file_path: str, output_format: str) -> None:
        print(">> Backing up MySQL database...")
