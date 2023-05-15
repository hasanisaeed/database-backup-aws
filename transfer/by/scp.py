from transfer.by.base import FileSender
import subprocess
from typing import Dict, Union, List


class ScpFileSender(FileSender):
    def __init__(self, host: str, port: int, username: str, password: str) -> None:
        self.host: str = host
        self.port: int = port
        self.username: str = username
        self.password: str = password

    def send_file(self, file_path: str) -> None:
        scp_command: List[Union[str, int]] = [
            'scp',
            '-P', str(self.port),
            file_path,
            f'{self.username}@{self.host}:'
        ]

        env: Dict[str, str] = {'SSHPASS': self.password}
        subprocess.run(scp_command, check=True, env=env)
