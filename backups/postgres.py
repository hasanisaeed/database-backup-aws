from backups import DBBackup

import subprocess

from connections.postgres import PostgresConnection


class PostgresBackup(DBBackup):
    def __init__(self, connection: PostgresConnection):
        self.connection = connection

    def backup(self, backup_file_path: str, output_format: str = 'gz') -> None:
        backup_strategy = self._get_backup_strategy(output_format)
        command = backup_strategy.get_backup_command(backup_file_path)
        self._execute_command(command)
        print("PostgreSQL database backup successful!")

    def _get_backup_strategy(self, output_format: str):
        if output_format == 'gz':
            return _GzBackupStrategy(self.connection)
        elif output_format == 'sql':
            return _SqlBackupStrategy(self.connection)
        else:
            raise ValueError("Invalid output format specified")

    def _execute_command(self, command: list) -> None:
        subprocess.run(command, check=True)


class _BackupStrategy:
    def __init__(self, connection: PostgresConnection):
        self.connection = connection

    def get_backup_command(self, backup_file_path: str) -> list:
        raise NotImplementedError


class _GzBackupStrategy(_BackupStrategy):
    def get_backup_command(self, backup_file_path: str) -> list:
        return [
            'pg_dump',
            '-h', self.connection.host,
            '-p', str(self.connection.port),
            '-U', self.connection.user,
            '-Fc',  # Output format as custom (gz)
            '-f', backup_file_path,
            self.connection.database,
        ]


class _SqlBackupStrategy(_BackupStrategy):
    def get_backup_command(self, backup_file_path: str) -> list:
        return [
            'pg_dump',
            '-h', self.connection.host,
            '-p', str(self.connection.port),
            '-U', self.connection.user,
            '-Fp',  # Output format as plain SQL
            '-f', backup_file_path,
            self.connection.database,
        ]
