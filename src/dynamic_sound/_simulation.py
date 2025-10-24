import os
from tqdm import tqdm
import numpy as np
import wave
from collections import deque
from scipy.signal import firwin2, lfilter

from ._environment import Air
from .acoustics.standards.ISO_9613_1_1993 import sound_speed, attenuation_coefficients, REFERENCE_TEMPERATURE, SOUND_SPEED
from .path import Path
from .sources import Source
from .microphones import MicrophoneArray
from scipy.spatial.transform import Rotation as R

class Simulation:
    def __init__(self, temperature=20, pressure=1, relative_humidity=50):
        self.air = Air(temperature=temperature, pressure=pressure, relative_humidity=relative_humidity)
        self._microphones = []
        self._sources = []

    def add_microphone(self, path:Path, microphone: MicrophoneArray):
        self._microphones.append((path, microphone))

    def add_source(self, path:Path, source:Source):
        self._sources.append((path, source))

    @staticmethod
    def _compute_emission(position_receiver, time_receiver, source_path, c=SOUND_SPEED):
        for path_index in range(len(source_path.positions) - 1):
            t0 = source_path.positions[path_index, 0]
            t1 = source_path.positions[path_index+1, 0]
            p0 = source_path.positions[path_index, 1:4]
            p1 = source_path.positions[path_index+1, 1:4]
            v = (p1 - p0) / (t1 - t0)

            if t0 <= time_receiver:
                d0 = position_receiver - p0

                A = np.dot(v, v) - c**2
                B = 2 * (c**2 * (time_receiver - t0) - np.dot(d0, v))
                C = np.dot(d0, d0) - (c * (time_receiver - t0))**2

                if A == 0:
                    if B == 0:
                        if C == 0:
                            print("ERROR: infinite values")
                            return None, None
                    else:
                        time_emission = (-C / B) + t0
                        if t0 <= time_emission < t1 and time_emission <= time_receiver:
                            position_emission = p0 + (v * (time_emission - t0))
                            return time_emission, position_emission
                else:
                    delta = B**2 - 4*A*C
                    if delta > 0:
                        sqrt_delta = np.sqrt(delta)
                        time_emission = min((-B - sqrt_delta) / (2*A) + t0, (-B + sqrt_delta) / (2*A) + t0)
                        if t0 <= time_emission < t1 and time_emission <= time_receiver:
                            position_emission = p0 + (v * (time_emission - t0))
                            return time_emission, position_emission
        return None, None

    def run(self):
        c = sound_speed(temperature=self.air.temperature, reference_temperature=REFERENCE_TEMPERATURE)

        for microphone_path, microphone in self._microphones:
            dst_path = os.path.dirname(microphone.file_path)
            if dst_path:
                os.makedirs(dst_path, exist_ok=True)

            with wave.open(microphone.file_path, mode="wb") as wave_file:
                wave_file.setnchannels(microphone.num_channels)
                wave_file.setsampwidth(microphone.sample_width)
                wave_file.setframerate(microphone.sample_rate)

                # air absorption filter
                filter_len = 11
                frequencies = np.linspace(0, microphone.sample_rate/2, num=20)  # freq bands resolution
                air_absorption_coefficients = attenuation_coefficients(
                    frequency=frequencies,
                    temperature=20 + 273.15,
                    relative_humidity=50,
                    pressure=1 * 101.325
                )

                out_buffer = [deque(np.zeros(filter_len), maxlen=filter_len) for _ in range(microphone.num_channels)]
                out_samples = np.zeros((int(microphone.sample_rate * microphone_path.duration), microphone.num_channels))

                for sample_index, time_receiver in tqdm([(index, index/microphone.sample_rate) for index in range(int(microphone.sample_rate * microphone_path.duration))]):
                    position_array, rotation_array = microphone_path.get_position(time_receiver)

                    for channel_index, microphone_position in enumerate(microphone.get_microphones()):
                        for source_path, source in self._sources:

                            rotation_receiver = R.from_quat(rotation_array)
                            position_receiver = position_array + rotation_receiver.apply(microphone_position[1:4])

                            time_emission, position_emission = self._compute_emission(position_receiver=position_receiver, time_receiver=time_receiver, source_path=source_path, c=c)

                            if time_emission is not None:
                                distance = np.linalg.norm(position_receiver - position_emission)

                                geometric_attenuation = 1.0 / distance
                                air_coeff = 10 ** (-air_absorption_coefficients * distance / 20)  # Convert coeffs in dB to linear scale
                                air_fir_coefficients = firwin2(filter_len, frequencies, air_coeff, fs=microphone.sample_rate)

                                out_buffer[channel_index].appendleft(source.get_sample(time_emission) * geometric_attenuation)
                                out_samples[sample_index, channel_index] += air_fir_coefficients.dot(out_buffer[channel_index])
                
                wave_file.writeframes((out_samples * (2**31 - 1)).astype(np.int32).tobytes())









