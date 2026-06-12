import math
import numpy as np
import soundfile as sf


def noise_generator(fs: int = 48000, amplitude: float = 1.0, length: int = 48000, filename: str = None, raw: bool = False, type: str = None) -> tuple[np.ndarray, dict]:
    """
    Generate white noise.
    Args:
      fs            : sampling rate in Hz
      amplitude     : amplitude of the white noise (0.0 to 1.0)
      length        : length of the white noise in samples
      filename      : base name for output files with extensions. If None, no files will be written
      type          : the subtype for the output file (ignored if filename is None)
    Returns:
        signal      : the generated white noise samples
        info        : a dictionary containing metadata about the generated white noise, including:
                        - samples: the total number of samples in the generated white noise
                        - duration: the duration of the white noise in seconds
    """


    signal = amplitude * (2.0 * np.random.rand(length) - 1.0)

    if filename is not None:
        sf.write(filename, signal, fs, subtype=type)

    info = {
        "samples": length,
        "duration": length / fs
    }
    
    return signal, info
