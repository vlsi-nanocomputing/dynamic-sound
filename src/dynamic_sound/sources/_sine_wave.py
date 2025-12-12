
from ._source import Source

import numpy as np

class SineWave(Source):
    def __init__(self, frequency, amplitude=1.0):
        super().__init__()
        self.amplitude = amplitude
        self.frequency = frequency

    def get_sample(self, time:float):
        return self.amplitude * np.sin(2 * np.pi * self.frequency * time)

