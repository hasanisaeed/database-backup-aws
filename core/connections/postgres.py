from typing import Dict, Union

from core.connections.base import DBConnection

from logger import Logger

logger = Logger.get_logger()


class PostgresConnection(DBConnection):
    def __init__(self, config: Dict[str, Union[str, int]]) -> None:
        self.host: str = config.get('host')
        self.port: int = config.get('port')
        self.database: str = config.get('database')
        self.user: str = config.get('user')
        self.password: str = config.get('password')
        self.container_name: str = config.get('container_name')

    def connect(self):
        # Add your Postgres-specific connection logic here
        logger.info(">> Connecting to Postgres database...")
        # Example: return psycopg2.connect(...)
