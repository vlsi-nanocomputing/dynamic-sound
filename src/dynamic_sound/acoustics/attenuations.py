
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
    OMNIDIRECTIONAL = 1
    SUBCARDIOID = 2
    CARDIOID = 3
    HYPERCARDBOID = 4
    SUPERCARDIOID = 5
    FIGURE8 = 6


def directivity(angle_rad, directivity):
    if directivity == DirectivityType.OMNIDIRECTIONAL:
        return 1.0
    elif directivity == DirectivityType.SUBCARDIOID:
        return 0.75 + 0.25 * np.cos(angle_rad)
    elif directivity == DirectivityType.CARDIOID:
        return 0.5 * (1 + np.cos(angle_rad))
    elif directivity == DirectivityType.HYPERCARDBOID:
        return np.abs(0.37 + 0.63 * np.cos(angle_rad))
    elif directivity == DirectivityType.SUPERCARDIOID:
        return np.abs(0.25 + 0.75 * np.cos(angle_rad))
    elif directivity == DirectivityType.FIGURE8:
        return np.abs(np.cos(angle_rad))
    else:
        raise ValueError(f"Unknown directivity type: {directivity}")

