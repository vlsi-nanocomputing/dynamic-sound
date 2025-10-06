from .standards.ISO_9613_1_1993 import SOUND_SPEED
import numpy as np

def wavelength(frequency, c=SOUND_SPEED):
    return c / frequency

def angular_frequency(frequency):
    return 2.0 * np.pi * frequency
