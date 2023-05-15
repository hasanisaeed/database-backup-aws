from transfer.tools import FileSender
import subprocess
from typing import Dict, Union, List


class ScpFileSender(FileSender):
    def __init__(self, config: Dict[str, Union[str, int]]) -> None:
        self.host: str = config['host']
        self.port: int = config['port']
        self.username: str = config['username']
        self.password: str = config['password']

    def _build_command(self, file_path: str) -> List[Union[str, int]]:
        return [
            'scp',
            '-P', str(self.port),
            file_path,
            f'{self.username}@{self.host}:'
        ]

    def _setup_env_file(self) -> Dict[str, str]:
        return {'SSHPASS': self.password}

    def _run_command(self, command: List[Union[str, int]]) -> None:
        env: Dict[str, str] = self._setup_env_file()
        subprocess.run(command, check=True, env=env)

    def send_file(self, file_path: str) -> None:
        command = self._build_command(file_path)
        self._run_command(command)
