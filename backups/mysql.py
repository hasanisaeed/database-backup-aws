from backups import DBBackup


class MySQLBackup(DBBackup):
    def backup(self) -> None:
        print("Backing up MySQL database...")
