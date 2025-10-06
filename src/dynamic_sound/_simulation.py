import os
from tqdm import tqdm
import time
import numpy as np
import wave
from collections import deque



from ._environment import Air
from .acoustics.standards.ISO_9613_1_1993 import sound_speed, attenuation_coefficients, REFERENCE_TEMPERATURE, SOUND_SPEED
from ._path import Path
from .sources import Source
from .microphones import MicrophoneArray

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
    def _get_emission(position_receiver, time_receiver, source_path, c=SOUND_SPEED):
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
                            time_emission = t0
                            return time_emission, p0 + (v * time_emission)
                    else:
                        time_emission = (-C / B) + t0
                        if t0 <= time_emission < t1 and time_emission <= time_receiver:
                            return time_emission, p0 + v * time_emission
                else:
                    delta = B**2 - 4*A*C
                    if delta == 0:
                        time_emission = -B / ( 2 * A )
                        if t0 <= time_emission < t1 and time_emission <= time_receiver:
                            return time_emission, p0 + v * time_emission
                    elif delta > 0:
                        sqrt_delta = np.sqrt(delta)
                        time_emission = min((-B - sqrt_delta) / (2*A) + t0, (-B + sqrt_delta) / (2*A) + t0)
                        if t0 <= time_emission < t1 and time_emission <= time_receiver:
                            return time_emission, p0 + v * time_emission
        return None, None
    
    @staticmethod
    def _precompute_pseud_A(frequencies, sample_rate):
        w = 2 * np.pi * frequencies / (sample_rate / 2)  # Compute air absorption filter
        L_air = 10  # Filter order - air absorption
        A = np.zeros((len(w),int(L_air/2 + 1)))  # Matrix A
        A[:,0] = 1
        for i in range(len(w)):
            for j in range(1,int(L_air/2 + 1)):
                A[i,j] = 2 * np.cos(w[i] * j)
        return np.linalg.inv(A.T.dot(A)).dot(A.T)

    @staticmethod
    def _compute_air_absorption_filter(pseud_A, airAbsorptionCoefficients, distance: float, numtaps: int) -> np.ndarray:
        filt_coeffs = np.empty(numtaps, np.float64)
        alpha = 10 ** (-airAbsorptionCoefficients * distance / 20)  # Convert coeffs in dB to linear scale
        filt_coeffs[int((numtaps+1)/2)-1:] = pseud_A.dot(alpha)
        filt_coeffs[0:int((numtaps+1)/2)-1] = np.flip(filt_coeffs[int((numtaps+1)/2):])
        return filt_coeffs

    def run(self):
        
        c = sound_speed(temperature=self.air.temperature, reference_temperature=REFERENCE_TEMPERATURE)
        

        for microphone_path, microphone in tqdm(self._microphones):
            os.makedirs(os.path.dirname(microphone.file_path), exist_ok=True)
            with wave.open(microphone.file_path, mode="wb") as wave_file:
                wave_file.setnchannels(microphone.num_channels)
                wave_file.setsampwidth(microphone.sample_width)
                wave_file.setframerate(microphone.sample_rate)

                # air absorption filter
                frequencies = np.linspace(0, microphone.sample_rate/2, num=20)  # freq bands resolution
                airAbsorptionCoefficients = attenuation_coefficients(
                    frequency=frequencies,
                    temperature=20 + 273.15,
                    relative_humidity=50,
                    pressure=1 * 101.325
                )
                pseud_A = self._precompute_pseud_A(frequencies, microphone.sample_rate)

                out_buffer = [deque(np.zeros(11), maxlen=11) for _ in range(microphone.num_channels)]
                out_samples = np.zeros((int(microphone.sample_rate * microphone_path.duration), microphone.num_channels))

                for sample_index, time_receiver in tqdm([(index, index/microphone.sample_rate) for index in range(int(microphone.sample_rate * microphone_path.duration))]):
                    for channel_index, microphone_position in enumerate(microphone.positions):
                        for source_path, source in self._sources:

                            position_receiver = microphone_path.get_position(time_receiver) + microphone_position[1:4]
                            time_emission, position_emission = self._get_emission(position_receiver=position_receiver, time_receiver=time_receiver, source_path=source_path, c=c)

                            if time_emission is not None:
                                distance = np.linalg.norm(position_receiver - position_emission)
                                geometric_attenuation = 1 / distance
                                air_filter_coeff = self._compute_air_absorption_filter(pseud_A, airAbsorptionCoefficients, distance, numtaps=11)

                                out_buffer[channel_index].appendleft( source.get_sample(time_emission) * geometric_attenuation )
                                out_samples[sample_index, channel_index] += air_filter_coeff.dot(out_buffer[channel_index])
                
                wave_file.writeframes((out_samples * (2**31 - 1)).astype(np.int32).tobytes())
                wave_file.close()








