import time
from abc import ABC, abstractmethod


class Strategy(ABC):

    @abstractmethod
    def calculate_date(self, **kwargs) -> int:
        pass


class RepeatEveryNMinutes(Strategy):
    sec = 60

    def __init__(self, n=1):
        super().__init__()
        self.n = n

    def calculate_date(self, execution_date):
        return execution_date + self.n * self.sec

