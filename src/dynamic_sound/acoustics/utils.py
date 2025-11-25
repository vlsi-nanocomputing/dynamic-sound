from .standards.ISO_9613_1_1993 import SOUND_SPEED
import numpy as np

def speed_of_sound(temperature=20, humidity=50):
    c = 331.3 + 0.606 * temperature + 0.0124 * humidity
    return c


def wavelength(frequency, c=SOUND_SPEED):
    return c / frequency

def angular_frequency(frequency):
    return 2.0 * np.pi * frequency
