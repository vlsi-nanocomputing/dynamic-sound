
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
    QUADCOPTER = 7

    @staticmethod
    def name(directivity):
        if directivity == DirectivityType.OMNIDIRECTIONAL:
            return "omnidirectional"
        elif directivity == DirectivityType.SUBCARDIOID:
            return "subcardioid"
        elif directivity == DirectivityType.CARDIOID:
            return "cardioid"
        elif directivity == DirectivityType.HYPERCARDBOID:
            return "hypercardioid"
        elif directivity == DirectivityType.SUPERCARDIOID:
            return "supercardioid"
        elif directivity == DirectivityType.FIGURE8:
            return "figure8"
        elif directivity == DirectivityType.QUADCOPTER:
            return "quadcopter"
        else:
            raise ValueError(f"Unknown directivity type: {directivity}")


def directivity(angle_rad, directivity):
    if directivity == DirectivityType.OMNIDIRECTIONAL:
        return 1.0
    elif directivity == DirectivityType.SUBCARDIOID:
        return 0.75 + 0.25 * np.cos(angle_rad)
    elif directivity == DirectivityType.CARDIOID:
        return (1 + np.cos(angle_rad)) / 2.0
    elif directivity == DirectivityType.HYPERCARDBOID:
        return np.abs(0.37 + 0.63 * np.cos(angle_rad))
    elif directivity == DirectivityType.SUPERCARDIOID:
        return np.abs(0.25 + 0.75 * np.cos(angle_rad))
    elif directivity == DirectivityType.FIGURE8:
        return np.abs(np.cos(angle_rad))
    elif directivity == DirectivityType.QUADCOPTER:
        """
        @article{heutschi2020synthesis,
        title={Synthesis of real world drone signals based on lab recordings},
        author={Heutschi, Kurt and Ott, Beat and Nussbaumer, Thomas and Wellig, Peter},
        journal={Acta Acustica},
        volume={4},
        number={6},
        pages={24},
        year={2020},
        publisher={EDP Sciences}
        }
        """
        angle_deg = (np.rad2deg(angle_rad) % 180) - 90
        return 10**((-0.0011 * angle_deg**2 + 0.194 * np.abs(angle_deg) - 8.55) / 20)
    else:
        raise ValueError(f"Unknown directivity type: {directivity}")


