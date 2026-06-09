
__all__ = [
    "geometric",
    "material_reflection",
    "DirectivityType"
    "directivity"
]

import numpy as np


def geometric(distance:float) -> float:
    if distance == 0:
        return 1.0
    return 1.0 / distance

def material_reflection(coeff):
    return 1.0

class DirectivityType:
    Omnidirectional = 1
    Subcardioid = 2
    Cardioid = 3
    Hypercardioid = 4
    Supercardioid = 5
    Figure8 = 6


def directivity(angle_rad, directivity):
    if directivity == DirectivityType.Omnidirectional:
        return 1.0
    elif directivity == DirectivityType.Subcardioid:
        return 0.75 + 0.25 * np.cos(angle_rad)
    elif directivity == DirectivityType.Cardioid:
        return 0.5 * (1 + np.cos(angle_rad))
    elif directivity == DirectivityType.Hypercardioid:
        return np.abs(0.37 + 0.63 * np.cos(angle_rad))
    elif directivity == DirectivityType.Supercardioid:
        return np.abs(0.25 + 0.75 * np.cos(angle_rad))
    elif directivity == DirectivityType.Figure8:
        return np.abs(np.cos(angle_rad))
    else:
        raise ValueError(f"Unknown directivity type: {directivity}")

