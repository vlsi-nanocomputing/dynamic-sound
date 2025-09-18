import numpy as np

def get_sinewave(frequency: float, duration: float, sample_rate: int) -> np.ndarray:
    t = np.arange(int(duration * sample_rate)) / sample_rate
    return np.sin(2 * np.pi * frequency * t)
