import numpy as np

class MicrophoneArray:
    def __init__(self, positions:list, file_path:str, sample_rate:int=48_000, sample_width=4):
        self.positions = np.array(positions, dtype=np.float64)
        self.num_channels = len(self.positions)
        self.sample_width = sample_width
        self.file_path = file_path
        self.sample_rate = sample_rate

    def get_microphones(self) -> np.ndarray:
        return self.positions

class Microphone(MicrophoneArray):
    def __init__(self, file_path:str, sample_rate:int=48_000, sample_width=4):
        position = [[0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0], ]
        super().__init__(position, file_path, sample_rate, sample_width)
