import numpy as np
from dynamic_sound.acoustics.attenuations import DirectivityType

class MicrophoneArray:
    def __init__(self, file_path:str, positions:list, sample_rate:int=48_000, sample_width=4, directivity:DirectivityType=DirectivityType.OMNIDIRECTIONAL):
        """Initializes a microphone array with the given parameters.

        Args:
            file_path (str): The path to the audio file will be created.
            positions (list): A list of microphone positions.
            sample_rate (int, optional): The sample rate of the audio file. Defaults to 48_000.
            sample_width (int, optional): The width of each sample in bytes. Defaults to 4.
            directivity (int|list, optional): The directivity type(s) of the microphones. Can be a single int for all microphones or a list of ints for each microphone. Defaults to None (omnidirectional).
        """
        self.positions = np.array(positions, dtype=np.float64)
        self.num_channels = len(self.positions)
        self.sample_width = sample_width
        self.file_path = file_path
        self.sample_rate = sample_rate
        self.directivity = np.ones(self.num_channels, dtype=np.uint8) * directivity

    def get_microphones(self) -> np.ndarray:
        """Returns the relative positions of the microphones as a numpy array of shape (num_channels, 7).

        Returns:
            np.ndarray: The relative positions of the microphones.
        """
        return self.positions

class Microphone(MicrophoneArray):
    def __init__(self, file_path:str, sample_rate:int=48_000, sample_width=4, directivity:DirectivityType=DirectivityType.OMNIDIRECTIONAL):
        """\Initializes a single microphone with the given parameters.

        Args:
            file_path (str): The path to the audio file will be created.
            sample_rate (int, optional): The sample rate of the audio file. Defaults to 48_000.
            sample_width (int, optional): The width of each sample in bytes. Defaults to 4.
            directivity (int|list, optional): The directivity type(s) of the microphone.
        """
        position = [[0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0], ]
        super().__init__(file_path=file_path,
                         positions=position,
                         sample_rate=sample_rate,
                         sample_width=sample_width,
                         directivity=directivity)
