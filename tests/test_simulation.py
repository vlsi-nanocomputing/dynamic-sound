from dynamic_sound import Simulation, Path
from dynamic_sound.microphones import MicrophoneArray
from dynamic_sound.sources import WhiteNoise, SineWave


def test_simulation():
    sim = Simulation(temperature=20, pressure=1, relative_humidity=50)
    sim.add_microphone(path=Path([
            [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
            [8.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
        ]), microphone=MicrophoneArray(positions=[
            (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        ], file_path="_tmp/recording.wav", sample_rate=48_000)
    )

    sin_signal = SineWave(frequency=2_000, duration=8.0, sample_rate=48_000, amplitude=1.0)
    sim.add_source(path=Path([
            [0.0, 3.0, 20.0, 1.0, 0.0, 0.0, 0.0, 0.0],
            [8.0, 3.0, -20.0, 1.0, 0.0, 0.0, 0.0, 0.0]
        ]), source=sin_signal
    )
    sim.add_source(path=Path([  # manual reflection
            [0.0, 3.0, 20.0, -1.0, 0.0, 0.0, 0.0, 0.0],
            [8.0, 3.0, -20.0, -1.0, 0.0, 0.0, 0.0, 0.0]
        ]), source=sin_signal
    )

    white_noise = WhiteNoise(duration=8.0, sample_rate=48_000, amplitude=1.0)
    sim.add_source(path=Path([
            [0.0, 3.0, 20.0, 1.0, 0.0, 0.0, 0.0, 0.0],
            [8.0, 3.0, -20.0, 1.0, 0.0, 0.0, 0.0, 0.0]
        ]), source=white_noise
    )
    sim.add_source(path=Path([  # manual reflection
            [0.0, 3.0, 20.0, -1.0, 0.0, 0.0, 0.0, 0.0],
            [8.0, 3.0, -20.0, -1.0, 0.0, 0.0, 0.0, 0.0]
        ]), source=white_noise
    )
    sim.run()


if __name__ == "__main__":
    test_simulation()
