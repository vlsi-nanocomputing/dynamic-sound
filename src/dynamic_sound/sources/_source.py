from abc import ABC, abstractmethod

class Source(ABC):

    @abstractmethod
    def __init__(self, sample_rate):
        super().__init__()
        self.sample_rate = sample_rate

    @abstractmethod
    def get_sample(self, time:float):
        """return the sample value at the specified time instant. Typically an interpolation technique is used here when the source is a sapmled signal.

        :param time: time of the requested signal sample.
        :type time: float
        """


