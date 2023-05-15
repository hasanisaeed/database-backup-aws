from typing import Type, TypeVar

from backups.base import DBBackup

T = TypeVar("T", bound=DBBackup)


class BackupFactory:
    def __init__(self, db_backup_strategy: Type[T]) -> None:
        self._db_backup_strategy = db_backup_strategy

    def create_backup(self) -> T:
        return self._db_backup_strategy()

# if __name__ == '__main__':
#     backup_factory = BackupFactory(PostgresBackup)
#     backup = backup_factory.create_backup()
#     backup.backup()
#
#     backup_factory = BackupFactory(MySQLBackup)
#     backup = backup_factory.create_backup()
#     backup.backup()
