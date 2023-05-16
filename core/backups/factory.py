from typing import Type, TypeVar

from databases.base import DBBackup

T = TypeVar("T", bound=DBBackup)


class BackupFactory:
    def __init__(self, db_backup_strategy: Type[T]) -> None:
        self._db_backup_strategy = db_backup_strategy

    def create_backup(self) -> T:
        return self._db_backup_strategy()
