import os
from tqdm import tqdm
import numpy as np
import wave
from collections import deque
from scipy.signal import firwin2, lfilter
import struct

from .environment import Air
from .acoustics import attenuations
from .acoustics.standards.ISO_9613_1_1993 import sound_speed, attenuation_coefficients, REFERENCE_TEMPERATURE, SOUND_SPEED
from .environment import Path
from .sources import Source, InterpolationType
from .microphones import MicrophoneArray
from scipy.spatial.transform import Rotation as R
from scipy.spatial.transform import Slerp

class Simulation:
    def __init__(self, temperature=20, pressure=1, relative_humidity=50):
        self.air = Air(temperature=temperature, pressure=pressure, relative_humidity=relative_humidity)
        self._microphones = []
        self._sources = []

    def add_microphone(self, path:Path, microphone: MicrophoneArray):
        self._microphones.append((path, microphone))

    def remove_microphones(self):
        self._microphones = []

    def add_source(self, path:Path, source:Source):
        self._sources.append((path, source))
    
    def remove_sources(self):
        self._sources = []

    @staticmethod
    def _incidence_angle_rad(p1, p2, r1):
        p1 = np.asarray(p1)
        p2 = np.asarray(p2)
        r1_inv = r1.inv()
        vec_global = p2 - p1
        vec_local = r1_inv.apply(vec_global)
        angle_rad = np.arccos(vec_local[0] / np.linalg.norm(vec_local))
        return angle_rad

    @staticmethod
    def _compute_emission(position_receiver, time_receiver, source_path, c=SOUND_SPEED):
        """Compute the time of emission and position of emission for a given receiver position and time, and a source path.
        This function solves the equation:
        ||position_receiver - position_emission|| = c * (time_receiver - time_emission)

        where position_emission is the position of the source at time_emission, which is given by the source path.
        The function iterates over the segments of the source path, and for each segment, it computes the time of emission and position of emission that satisfy the equation. If a valid solution is found (i.e., time_emission is within the segment and time_emission <= time_receiver), it returns the time of emission and position of emission. If no valid solution is found after iterating over all segments, it returns None, None.
        """

        for path_index in range(len(source_path.positions) - 1):
            t0 = source_path.positions[path_index, 0]
            t1 = source_path.positions[path_index+1, 0]
            p0 = source_path.positions[path_index, 1:4]
            p1 = source_path.positions[path_index+1, 1:4]
            q0 = source_path.positions[path_index, 4:8]
            q1 = source_path.positions[path_index+1, 4:8]
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
                            return None, None, None
                    else:
                        time_emission = (-C / B) + t0
                        if t0 <= time_emission < t1 and time_emission <= time_receiver:
                            position_emission = p0 + (v * (time_emission - t0))
                            rotation_emission = Slerp([t0, t1], R.from_quat([q0, q1], scalar_first=True))(time_emission)
                            return time_emission, position_emission, rotation_emission
                else:
                    delta = B**2 - 4*A*C
                    if delta > 0:
                        sqrt_delta = np.sqrt(delta)
                        time_emission = min((-B - sqrt_delta) / (2*A) + t0, (-B + sqrt_delta) / (2*A) + t0)
                        if t0 <= time_emission < t1 and time_emission <= time_receiver:
                            position_emission = p0 + (v * (time_emission - t0))
                            rotation_emission = Slerp([t0, t1], R.from_quat([q0, q1], scalar_first=True))(time_emission)
                            return time_emission, position_emission, rotation_emission
        return None, None, None

    def run(self):
        c = sound_speed(temperature=self.air.temperature+273.15)

        for microphone_path, microphone in self._microphones:
            dst_path = os.path.dirname(microphone.file_path)
            if dst_path:
                os.makedirs(dst_path, exist_ok=True)

            with wave.open(microphone.file_path, mode="wb") as wave_file:
                wave_file.setnchannels(microphone.num_channels)
                wave_file.setsampwidth(microphone.sample_width)
                wave_file.setframerate(microphone.sample_rate)

                # air absorption filter
                filter_len = 33
                frequencies = np.linspace(0, microphone.sample_rate/2, num=32)  #TODO: num=512)
                air_absorption_coefficients = attenuation_coefficients(
                    frequency=frequencies,
                    temperature=self.air.temperature + 273.15,
                    relative_humidity=self.air.relative_humidity,
                    pressure=self.air.pressure * 101.325
                )

                out_buffer = [deque(np.zeros(filter_len), maxlen=filter_len) for _ in range(microphone.num_channels)]
                out_samples = np.zeros((int(microphone.sample_rate * microphone_path.duration), microphone.num_channels))

                for sample_index, time_receiver in tqdm([(index, (index/microphone.sample_rate)+ microphone_path.start_time) for index in range(int(microphone.sample_rate * microphone_path.duration))]):
                    position_array, rotation_array = microphone_path.get_position(time_receiver)

                    for channel_index, microphone_position in enumerate(microphone.get_microphones()):
                        for source_path, source in self._sources:

                            rotation_receiver = R.from_quat(rotation_array, scalar_first=True)
                            position_receiver = position_array + rotation_receiver.apply(microphone_position[0:3])

                            time_emission, position_emission, rotation_emission = self._compute_emission(
                                position_receiver=position_receiver,
                                time_receiver=time_receiver,
                                source_path=source_path,
                                c=c
                            )
                            
                            if time_emission is not None:

                                distance = np.linalg.norm(position_receiver - position_emission)

                                emitter_angle = Simulation._incidence_angle_rad(p1=position_emission, p2=position_receiver, r1=rotation_emission)
                                receiver_angle = Simulation._incidence_angle_rad(p1=position_receiver, p2=position_emission, r1=rotation_receiver)

                                attenuation_geom = attenuations.geometric(distance)
                                attennuation_dir_emitter = attenuations.directivity(emitter_angle, source.directivity)
                                attenuation_dir_receiver = attenuations.directivity(receiver_angle, microphone.directivity[channel_index])
                                
                                air_coeff = 10 ** (-air_absorption_coefficients * distance / 20.0)  # Convert coeffs in dB to linear scale
                                air_fir_coefficients = firwin2(filter_len, frequencies, air_coeff, fs=microphone.sample_rate)

                                out_buffer[channel_index].appendleft(source.get_sample(time_emission) * attenuation_geom * attennuation_dir_emitter * attenuation_dir_receiver)
                                out_samples[sample_index, channel_index] += air_fir_coefficients.dot(out_buffer[channel_index])
                
                interleaved = (np.clip(out_samples, -1.0, 1.0) * np.iinfo(np.int32).max).astype(np.int32).reshape(-1)
                wave_file.writeframes(struct.pack("<" + "i" * len(interleaved), *interleaved)) # int32 (little-endian)
