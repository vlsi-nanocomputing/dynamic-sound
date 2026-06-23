from dynamic_sound.acoustics.attenuations import DirectivityType

from ._source import Source, InterpolationType

import numpy as np

class WhiteNoise(Source):
    def __init__(self, duration, sample_rate=48_000, amplitude=1.0,
                 interpolation:int=InterpolationType.LINEAR, directivity:DirectivityType=DirectivityType.OMNIDIRECTIONAL):
        super().__init__(directivity=directivity)
        self.sample_rate = sample_rate
        self.signal = amplitude * np.random.uniform(-1.0, 1.0, int(duration * sample_rate))
        self.interpolation = interpolation

    def get_sample(self, time:float):
        if self.interpolation == InterpolationType.LINEAR:
            time_int = int(time * self.sample_rate)
            time_frac = time * self.sample_rate - time_int
            return (1.0 - time_frac) * self.signal[time_int] + time_frac * self.signal[time_int + 1]
        else:
            raise NotImplementedError("Interpolation type not implemented")
    
