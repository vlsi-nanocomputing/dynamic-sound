
from ._source import Source

import numpy as np

class SineWave(Source):
    def __init__(self, frequency, duration, sample_rate=48_000, amplitude=1.0):
        super().__init__(sample_rate=sample_rate)
        self.signal = amplitude * np.sin(2 * np.pi * frequency * np.linspace(0, duration, int(sample_rate * duration), endpoint=False))

    def get_sample(self, time:float):
        time_int = int(time * self.sample_rate)
        time_frac = time * self.sample_rate - time_int
        return (1.0 - time_frac) * self.signal[time_int] + time_frac * self.signal[time_int + 1]
    
