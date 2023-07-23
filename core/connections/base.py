import abc


class DBConnection(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def connect(self):
        ...
