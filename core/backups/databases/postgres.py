import subprocess

from core.backups.databases.base import DBBackup
from core.connections.postgres import PostgresConnection

from logger import Logger

logger = Logger.get_logger()


class PostgresBackup(DBBackup):
    def __init__(self, connection: PostgresConnection):
        self.connection = connection

    def backup(self, backup_file_path: str, output_format: str = 'gz') -> bool:
        backup_strategy = self._get_backup_strategy(output_format)
        command = backup_strategy.build_backup_command(backup_file_path)
        return self._execute_command(command)

    def _get_backup_strategy(self, output_format: str):
        if output_format == 'gz':
            return _GzBackupStrategy(self.connection)
        elif output_format == 'sql':
            return _SqlBackupStrategy(self.connection)
        else:
            logger.error(f">> Invalid output format ({output_format}) specified.")
            raise ValueError(f">> Invalid output format ({output_format}) specified.")

    def _execute_command(self, command: list) -> bool:
        env = self._setup_env_file()
        try:
            subprocess.run(command, check=True, env=env)
        except subprocess.CalledProcessError:
            logger.error(">> Connecting to the database failed.")
            return False

        logger.info(">> PostgreSQL database backup successful!")
        return True

    def _setup_env_file(self) -> dict:
        env = {'PGPASSWORD': self.connection.password}
        return env


class _BackupStrategy:
    def __init__(self, connection: PostgresConnection):
        self.connection = connection

    def build_backup_command(self, backup_file_path: str) -> list:
        raise NotImplementedError


class _GzBackupStrategy(_BackupStrategy):
    def __init__(self, connection: PostgresConnection):
        super().__init__(connection)

    def build_backup_command(self, backup_file_path: str) -> list:
        command = [
            'pg_dump',
            '-h', self.connection.host,
            '-p', str(self.connection.port),
            '-U', self.connection.user,
            '-Fc',  # Output format as custom (gz)
            '-f', backup_file_path,
            self.connection.database,
        ]

        return command


class _SqlBackupStrategy(_BackupStrategy):
    def build_backup_command(self, backup_file_path: str) -> list:
        return [
            'pg_dump',
            '-h', self.connection.host,
            '-p', str(self.connection.port),
            '-U', self.connection.user,
            '-Fp',  # Output format as plain SQL
            '-f', backup_file_path,
            self.connection.database,
        ]
