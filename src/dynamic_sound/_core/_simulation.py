from dynamic_sound._core._environment import sound_attenuation
from dynamic_sound._core._time_emission import time_emission
from dynamic_sound._core._path import get_position
from dynamic_sound._core._source import get_sinewave
from dynamic_sound._core._microphone_array import CustomArray

import os
from tqdm import tqdm
import time
import numpy as np
import wave


class Simulation:
    def __init__(self, sample_rate: int, time_start: float, time_duration: float):
        self.sample_rate = sample_rate
        self.time_start = time_start
        self.time_duration = time_duration
        self.mic_array = None
        self.path_mic = None
        self.samples = None
    
    def add_source(self, samples: np.ndarray, path: tuple):
        self.path_src = path
        self.samples = samples

    def add_microphones(self, microphones: np.ndarray, path: tuple):
        self.path_mic = path   
        self.mic_array = microphones     

    def run(self, output_filename: str):

        os.makedirs(os.path.dirname(output_filename), exist_ok=True)

        num_channels = len(self.mic_array)
        with wave.open(output_filename, mode="wb") as wf:
            wf.setnchannels(num_channels)
            wf.setsampwidth(4)
            wf.setframerate(self.sample_rate)

            samples_out = np.zeros((int(self.sample_rate * self.time_duration), num_channels))
            for index, tr in tqdm([(index, self.time_start + index/self.sample_rate) for index in range(int(self.sample_rate * self.time_duration))]):
                for channel_index, mic in enumerate(self.mic_array):
                    pr = get_position(self.path_mic, tr) + np.array(mic)
                    te, pe = time_emission(pr, tr, self.path_src)

                    attenuation = sound_attenuation(np.linalg.norm(pr - pe)) if pe is not None else 1.0
                    te_int = int(te * self.sample_rate) if te is not None else None
                    te_frac = (te * self.sample_rate - te_int) if te is not None else None
                    samples_out[index, channel_index] = (((1.0 - te_frac) * self.samples[te_int]) + (te_frac * self.samples[te_int + 1])) * attenuation if te is not None else 0.0

            wf.writeframes((samples_out * (2**31 - 1)).astype(np.int32).tobytes())
            wf.close()
