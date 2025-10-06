import numpy as np
import os

class Path:
    def __init__(self, positions=None):
        self.positions = None
        self.duration = 0.0
        if positions is not None:
            self.positions = np.array(positions, dtype=np.float64)
            self.duration = self.positions[-1][0] - self.positions[0][0]

    def save_path(self, file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        np.savetxt(file_path, self.positions, delimiter=',')

    def load_path(self, file_path):
        self.positions = np.genfromtxt(file_path, delimiter=',', dtype=np.float64)
        self.duration = self.positions[-1][0] - self.positions[0][0]
    
    def get_position(self, time):
        if self.positions[0, 0] <= time < self.positions[-1, 0]:
            for index in range(len(self.positions) - 1):
                t0 = self.positions[index, 0]
                p0 = self.positions[index, 1:4]

                t1 = self.positions[index+1, 0]
                p1 = self.positions[index+1, 1:4]

                if t0 <= time < t1:
                    alpha = (time - t0) / (t1 - t0)
                    return p0 + alpha * (p1 - p0)

        return None
