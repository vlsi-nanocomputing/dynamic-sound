from abc import ABC, abstractmethod
from dynamic_sound.acoustics.attenuations import DirectivityType

class InterpolationType:
    NONE = 0
    LINEAR = 1
    SINC = 2

class Source(ABC):

    @abstractmethod
    def __init__(self, directivity:DirectivityType=DirectivityType.OMNIDIRECTIONAL):
        super().__init__()
        self.directivity = directivity

    @abstractmethod
    def get_sample(self, time:float):
        """return the sample value at the specified time instant. Typically an interpolation technique is used here when the source is a sapmled signal.

        :param time: time of the requested signal sample.
        :type time: float
        """


