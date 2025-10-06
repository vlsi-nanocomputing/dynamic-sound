from .standards.ISO_9613_1_1993 import SOUND_SPEED


def frequency(frequency, velocity_source, velocity_receiver, soundspeed=SOUND_SPEED):
    return (soundspeed + velocity_receiver) / (soundspeed + velocity_source) * frequency

def velocity(f1, f2, c=SOUND_SPEED):
    return c * (f2 - f1) / (f2 + f1)
