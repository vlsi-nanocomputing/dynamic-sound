
from ._source import Source, InterpolationType

import librosa
import numpy as np

class AudioFile(Source):
    def __init__(self, filename, sample_rate=None, gain_db=0.0, loop=True, interpolation:int=InterpolationType.LINEAR):
        super().__init__()
        self.signal, self.sample_rate = librosa.load(filename, sr=sample_rate, mono=True)
        self.loop = loop
        self.length = len(self.signal)
        if gain_db != 0.0:
            self.signal = self.signal * 10**(gain_db / 20.0)
        self.interpolation = interpolation

    def get_sample(self, time:float):
        if self.interpolation == InterpolationType.NONE:
            time_int = int(time * self.sample_rate)
            if self.loop:
                return self.signal[time_int % self.length]
            else:
                if time_int >= self.length:
                    return 0.0
                else:
                    return self.signal[time_int]
        elif self.interpolation == InterpolationType.LINEAR:
            time_int = int(time * self.sample_rate)
            if self.loop == False and time_int >= self.length-1:
                return 0.0
            
            time_frac = time * self.sample_rate - time_int
            return (1.0 - time_frac) * self.signal[time_int % self.length] + time_frac * self.signal[(time_int + 1) % self.length]
        elif self.interpolation == InterpolationType.SINC:
            if self.loop == False and time >= self.length / self.sample_rate:
                return 0.0
            
            time_int = int(time * self.sample_rate)
            sample_pos = time * self.sample_rate
            hann_window = np.hanning(64)
            sinc_range = np.arange(-32, 32)
            sinc_func = np.sinc(sinc_range - (sample_pos - time_int))
            sinc_func *= hann_window
            sinc_func /= np.sum(sinc_func)
            sample_indices = (time_int + sinc_range) % self.length
            return np.sum(self.signal[sample_indices] * sinc_func)
        else:
            raise NotImplementedError("Interpolation type not implemented")
