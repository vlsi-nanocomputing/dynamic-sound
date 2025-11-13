
from ._source import Source

import librosa
import numpy as np

class AudioFile(Source):
    def __init__(self, filename, sample_rate=None, gain_db=0.0, loop=True):
        super().__init__()
        self.signal, self.sample_rate = librosa.load(filename, sr=sample_rate, mono=True)
        self.loop = loop
        self.length = len(self.signal)
        if gain_db != 0.0:
            self.signal = self.signal * 10**(gain_db / 20.0)

    def get_sample(self, time:float):
        time_int = int(time * self.sample_rate)
        if self.loop == False and time_int >= self.length-1:
            return 0.0
        
        time_frac = time * self.sample_rate - time_int
        return (1.0 - time_frac) * self.signal[time_int % self.length] + time_frac * self.signal[(time_int + 1) % self.length]
