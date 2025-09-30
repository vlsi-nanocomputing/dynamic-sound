import numpy as np

def get_sinewave(frequency: float, duration: float, sample_rate: int) -> np.ndarray:
    t = np.arange(int(duration * sample_rate)) / sample_rate
    return np.sin(2 * np.pi * frequency * t)

def get_white_noise(duration: float, sample_rate: int) -> np.ndarray:
    return np.random.normal(0, 1, int(duration * sample_rate))


