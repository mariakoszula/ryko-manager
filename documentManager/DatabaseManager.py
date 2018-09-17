from abc import ABC, abstractmethod


class DatabaseManager(ABC):

    def __init__(self):
        super.__init__()

    @abstractmethod
    def update_row(self):
        pass

    @abstractmethod
    def modify_row(self):
        pass
