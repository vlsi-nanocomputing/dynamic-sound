from abc import ABC, abstractmethod

class Source(ABC):

    @abstractmethod
    def __init__(self, sample_rate):
        super().__init__()
        self.sample_rate = sample_rate

    @abstractmethod
    def get_sample(self, time:float):
        pass


