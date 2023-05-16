import abc


class DBBackup(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def backup(self, backup_file_path: str, output_format: str) -> None:
        ...
