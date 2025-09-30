from dynamic_sound._core._environment import sound_attenuation
from dynamic_sound._core._time_emission import time_emission
from dynamic_sound._core._path import get_position
from dynamic_sound._core._environment import soundspeed, air_absorption_coefficients, precompute_pseud_A, compute_air_absorption_filter


import os
from tqdm import tqdm
import time
import numpy as np
import wave
from collections import deque


class Simulation:
    def __init__(self, sample_rate: int, time_start: float, time_duration: float):
        self.sample_rate = sample_rate
        self.time_start = time_start
        self.time_duration = time_duration
        self.mic_array = None
        self.path_mic = None
        self.sources = []
        self.frequencies = np.linspace(0, self.sample_rate/2, num=20)  # num freq bands resolution
        
        self.sound_speed = None
        self.temperature = None
        self.relative_humidity = None
        self.pseud_A = None
        self.airAbsorptionCoefficients = None

    def add_source(self, samples: np.ndarray, path: tuple):
        self.sources.append((samples, path))

    def add_microphones(self, microphones: np.ndarray, path: tuple):
        self.path_mic = path   
        self.mic_array = microphones     

    def set_environment(self, temperature, pressure, relative_humidity):
        self.temperature = temperature
        self.pressure = pressure
        self.relative_humidity = relative_humidity

        self.sound_speed = soundspeed(temperature)
        
        self.airAbsorptionCoefficients = air_absorption_coefficients(
            f=self.frequencies,
            T=self.temperature+273.15,
            pa=self.pressure*101.325,
            hr=self.relative_humidity
        )

        self.pseud_A = precompute_pseud_A(self.frequencies, self.sample_rate)
        

    def run(self, output_filename: str):

        os.makedirs(os.path.dirname(output_filename), exist_ok=True)

        num_channels = len(self.mic_array)
        with wave.open(output_filename, mode="wb") as wf:
            wf.setnchannels(num_channels)
            wf.setsampwidth(4)
            wf.setframerate(self.sample_rate)

            out_buffer = [deque(np.zeros(11), maxlen=11) for _ in range(num_channels)]
            out_samples = np.zeros((int(self.sample_rate * self.time_duration), num_channels))
            for index, tr in tqdm([(index, self.time_start + index/self.sample_rate) for index in range(int(self.sample_rate * self.time_duration))]):
                for channel_index, mic in enumerate(self.mic_array):
                    for samples, path_src in self.sources:
                        pr = get_position(self.path_mic, tr) + np.array(mic)
                        te, pe = time_emission(pr, tr, path_src, c=self.sound_speed)

                        if te is not None:
                            distance = np.linalg.norm(pr - pe)
                            attenuation = sound_attenuation(distance)
                            air_filter_coeff = compute_air_absorption_filter(self.pseud_A, self.airAbsorptionCoefficients, distance, numtaps=11)

                            te_int = int(te * self.sample_rate)
                            te_frac = (te * self.sample_rate - te_int)
                            out_buffer[channel_index].appendleft( (((1.0 - te_frac) * samples[te_int]) + (te_frac * samples[te_int + 1])) * attenuation )
                            out_samples[index, channel_index] += air_filter_coeff.dot(out_buffer[channel_index])
                        else:
                            out_samples[index, channel_index] += 0.0

            wf.writeframes((out_samples * (2**31 - 1)).astype(np.int32).tobytes())
            wf.close()


if __name__ == "__main__":
    from dynamic_sound import HedraPhone_v2, get_white_noise

    # simulation parameters
    sample_rate = 48_000
    sim = Simulation(sample_rate=sample_rate, time_start=0.0, time_duration=8.0)
    sim.set_environment(temperature=20, pressure=1, relative_humidity=50)

    # microphones
    # sim.add_microphones(microphones=HedraPhone_v2.get_microphones(), path=(
    #     (0.0, (0, 0, 1.0)),
    #     (8.0, (0, 0, 1.0))
    # ))
    sim.add_microphones(np.array([[0.0, 0.0, 0.0]]), path=(
        (0.0, (0, 0, 1.0)),
        (8.0, (0, 0, 1.0))
    ))

    # sound source
    #samples = get_sinewave(frequency=2_000, duration=10, sample_rate=sample_rate)
    samples = get_white_noise(duration=10, sample_rate=sample_rate)
    sim.add_source(samples=samples, path=(
        (0.0, (3, 20, 1)),
        (8.0, (3, -20, 1))
    ))

    # # image source
    sim.add_source(samples=samples, path=(
        (0.0, (3, 20, -1)),
        (8.0, (3, -20, -1))
    ))

    # run simulation
    sim.run(output_filename="output.wav")