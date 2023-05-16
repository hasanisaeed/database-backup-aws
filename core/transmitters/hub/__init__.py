from abc import ABC, abstractmethod


class FileSender(ABC):
    @abstractmethod
    def send_file(self, file_path: str) -> None:
        ...
