
from dynamic_sound.acoustics.attenuations import DirectivityType

from ._source import Source

import numpy as np

class SineWave(Source):
    def __init__(self, frequency, amplitude=1.0, directivity:DirectivityType=DirectivityType.OMNIDIRECTIONAL):
        super().__init__(directivity=directivity)
        self.amplitude = amplitude
        self.frequency = frequency

    def get_sample(self, time:float):
        return self.amplitude * np.sin(2 * np.pi * self.frequency * time)

