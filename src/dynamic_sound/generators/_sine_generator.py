import math
import numpy as np
import soundfile as sf


def sine_generator(f: float, fs: int = 48000, amplitude: float = 1.0, length: int|str = "period", filename: str = None, raw: bool = False, type: str = None) -> tuple[np.ndarray, dict]:
    """
    Generate a sine wave.
    Args:
      f             : frequency in Hz
      fs            : sampling rate in Hz
      amplitude     : amplitude of the sine wave (0.0 to 1.0)
      length        : length of the sine wave in samples or "period" for one period
      filename      : base name for output files with extensions. If None, no files will be written
      type          : the subtype for the output file (ignored if filename is None)
    Returns:
        signal      : the generated sine wave samples
        info        : a dictionary containing metadata about the generated sine wave, including:
                        - frequency: the frequency of the sine wave in Hz
                        - samples: the total number of samples in the generated sine wave
                        - duration: the duration of the sine wave in seconds
                        - cycles: the number of complete cycles in the generated sine wave
    """

    if length == "period":
        # Minimum periodic length
        gcd = math.gcd(int(round(fs)), int(round(f)))
        N = fs // gcd
    else:
        N = length
    n = np.arange(N)

    # Generate sine
    signal = amplitude * np.sin(2 * np.pi * f * n / fs)

    # save to file
    if filename is not None:
        sf.write(filename, signal, fs, subtype=type)

    info = {
        "frequency": f,
        "samples": N,
        "duration": N / fs,
        "cycles": f * (N / fs)
    }
    
    return signal, info
