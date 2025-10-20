
from ._source import Source

import numpy as np

class SineWave(Source):
    def __init__(self, frequency, sample_rate=48_000, amplitude=1.0):
        super().__init__(sample_rate=sample_rate)
        self.amplitude = amplitude
        self.frequency = frequency

    def get_sample(self, time:float):
        return self.amplitude * np.sin(2 * np.pi * self.frequency * time)
    
