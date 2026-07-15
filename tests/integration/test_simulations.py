import pytest
import os

import dynamic_sound as ds

@pytest.fixture
def simulation_empty():
    return ds.Simulation()

def test_white_noise_with_reflection(simulation_empty):
    sim = simulation_empty
    sim.add_microphone(
        path=ds.Path([
            [0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0],
            [5.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0]]),
        microphone=ds.microphones.Microphone(file_path=os.path.join("tests", "_tmp", "test_white_noise_with_reflection.wav"), sample_rate=8000)
    )
    sim.add_source(
        path=ds.Path([
            [0.0, 3.0, +20.0, 1.0, 1.0, 0.0, 0.0, 0.0],
            [5.0, 3.0, -20.0, 1.0, 1.0, 0.0, 0.0, 0.0]
        ]),
        source=ds.sources.WhiteNoise(duration=5.0, sample_rate=48000, amplitude=1.5)
    )
    sim.add_source(
        path=ds.Path([
            [0.0, 3.0, +20.0, -1.0, 1.0, 0.0, 0.0, 0.0],
            [10.0, 3.0, -20.0, -1.0, 1.0, 0.0, 0.0, 0.0]
        ]),
        source=ds.sources.WhiteNoise(duration=5.0, sample_rate=48000, amplitude=1.5)
    )
    sim.run()
    assert os.path.exists(os.path.join("tests", "_tmp", "test_white_noise_with_reflection.wav"))


