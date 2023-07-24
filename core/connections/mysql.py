from typing import Union, Dict

from core.connections.base import DBConnection

from logger import Logger

logger = Logger.get_logger()


class MySQLConnection(DBConnection):

    def __init__(self, config: Dict[str, Union[str, int]]) -> None:
        self.host: str = config['host']
        self.port: int = config['port']
        self.database: str = config['database']
        self.user: str = config['user']
        self.password: str = config['password']

    def connect(self):
        # Add your MySQL-specific connection logic here
        logger.info(">> Connecting to MySQL database...")
        # Example: return mysql.connector.connect(...)
