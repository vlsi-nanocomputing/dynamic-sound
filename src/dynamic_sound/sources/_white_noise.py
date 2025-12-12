from ._source import Source

import numpy as np

class WhiteNoise(Source):
    def __init__(self, duration, sample_rate=48_000, amplitude=1.0):
        super().__init__()
        self.sample_rate = sample_rate
        self.signal = amplitude * np.random.uniform(-1.0, 1.0, int(duration * sample_rate))

    def get_sample(self, time:float):
        time_int = int(time * self.sample_rate)
        time_frac = time * self.sample_rate - time_int
        return (1.0 - time_frac) * self.signal[time_int] + time_frac * self.signal[time_int + 1]
    
