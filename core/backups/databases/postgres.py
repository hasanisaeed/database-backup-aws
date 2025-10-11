import subprocess
from core.connections.postgres import PostgresConnection
from logger import Logger

logger = Logger.get_logger()


class PostgresBackup:
    """
    Performs PostgreSQL backup either via a direct host connection 
    or by executing pg_dump inside a Docker container.
    The method is chosen based on the presence of 'container_name' in the config.
    """

    def __init__(self, connection: PostgresConnection):
        self.connection = connection

    def backup(self, backup_file_path: str, output_format: str = 'gz') -> bool:
        """Dispatcher method to select the backup strategy."""
        if self.connection.container_name:
            logger.info(">> Docker container name found. Using 'docker exec' backup method.")
            return self._backup_via_docker(backup_file_path, output_format)
        else:
            logger.info(">> No container name found. Using host 'pg_dump' backup method.")
            return self._backup_via_host(backup_file_path, output_format)

    def _backup_via_docker(self, backup_file_path: str, output_format: str) -> bool:
        """Backup using 'docker exec' to run pg_dump inside the container."""
        strategy = self._get_backup_strategy(output_format)
        command = strategy.build_docker_command()

        try:
            logger.info(f">> Running backup command inside container '{self.connection.container_name}'...")
            process = subprocess.run(
                command,
                check=True,
                capture_output=True
            )
            with open(backup_file_path, 'wb') as f:
                f.write(process.stdout)
        except subprocess.CalledProcessError as e:
            logger.error(">> Docker backup command failed.")
            logger.error(f">> Stderr: {e.stderr.decode('utf-8', errors='ignore')}")
            return False
        except FileNotFoundError:
            logger.error(">> 'docker' command not found. Is Docker installed and in your PATH?")
            return False

        logger.info(">> PostgreSQL (Docker) database backup successful!")
        return True

    def _backup_via_host(self, backup_file_path: str, output_format: str) -> bool:
        """Backup using the host's pg_dump to connect directly."""
        strategy = self._get_backup_strategy(output_format)
        command = strategy.build_host_command(backup_file_path)
        env = {'PGPASSWORD': self.connection.password}

        try:
            subprocess.run(command, check=True, env=env)
        except subprocess.CalledProcessError:
            logger.error(">> Connecting to the database failed (host method).")
            return False
        except FileNotFoundError:
            logger.error(">> 'pg_dump' command not found. Is postgresql-client installed?")
            return False

        logger.info(">> PostgreSQL (Host) database backup successful!")
        return True

    def _get_backup_strategy(self, output_format: str):
        if output_format == 'gz':
            return _GzBackupStrategy(self.connection)
        elif output_format == 'sql':
            return _SqlBackupStrategy(self.connection)
        else:
            logger.error(f">> Invalid output format ({output_format}) specified.")
            raise ValueError(f">> Invalid output format ({output_format}) specified.")


class _BackupStrategy:
    def __init__(self, connection: PostgresConnection):
        self.connection = connection


class _GzBackupStrategy(_BackupStrategy):
    def build_host_command(self, backup_file_path: str) -> list:
        """Builds the direct pg_dump command for the host."""
        return [
            'pg_dump',
            '-h', self.connection.host,
            '-p', str(self.connection.port),
            '-U', self.connection.user,
            '-Fc',
            '-f', backup_file_path,
            self.connection.database,
        ]

    def build_docker_command(self) -> list:
        """Builds the 'docker exec' command."""
        return [
            'docker', 'exec',
            '-e', f'PGPASSWORD={self.connection.password}',
            self.connection.container_name,
            'pg_dump',
            '-U', self.connection.user,
            '-d', self.connection.database,
            '-Fc'
        ]


class _SqlBackupStrategy(_BackupStrategy):
    def build_host_command(self, backup_file_path: str) -> list:
        """Builds the direct pg_dump command for the host."""
        return [
            'pg_dump',
            '-h', self.connection.host,
            '-p', str(self.connection.port),
            '-U', self.connection.user,
            '-Fp',
            '-f', backup_file_path,
            self.connection.database,
        ]

    def build_docker_command(self) -> list:
        """Builds the 'docker exec' command."""
        return [
            'docker', 'exec',
            '-e', f'PGPASSWORD={self.connection.password}',
            self.connection.container_name,
            'pg_dump',
            '-U', self.connection.user,
            '-d', self.connection.database,
            '-Fp'
        ]