import pytest
import os
import numpy as np

import dynamic_sound as ds


class TestMicrophone:

    def test_microphone_init(self):
        microphone = ds.microphones.Microphone(file_path=os.path.join("tests", "_tmp", "test_microphone_init.wav"), sample_rate=44100)
        assert isinstance(microphone, ds.microphones.Microphone)
        assert microphone.sample_rate == 44100
        assert microphone.positions == pytest.approx(np.array([[0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]]))


class TestMicrophoneArray:

    def test_microphone_array_init(self):
        positions = [[0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
                     [1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0]]
        microphone_array = ds.microphones.MicrophoneArray(
            file_path=os.path.join("tests", "_tmp", "test_microphone_array_init.wav"),
            positions=positions,
            sample_rate=44100)
        assert isinstance(microphone_array, ds.microphones.MicrophoneArray)
        assert microphone_array.sample_rate == 44100
        assert microphone_array.positions == pytest.approx(np.array(positions))


class TestHedraphone:
    
    def test_hedraphone_init(self):
        microphone = ds.microphones.Hedraphone(file_path=os.path.join("tests", "_tmp", "test_hedraphone_init.wav"), sample_rate=44100, rnd_angle=5.0, rnd_position=0.01)
        assert isinstance(microphone, ds.microphones.Hedraphone)
        assert isinstance(microphone, ds.microphones.MicrophoneArray)
        assert microphone.sample_rate == 44100
    
    def test_plot_figure(self):
        microphone = ds.microphones.Hedraphone(file_path=os.path.join("tests", "_tmp", "test_hedraphone_plot_figure.wav"), sample_rate=44100)
        fig = microphone.plot_figure(show=False)
        assert fig is not None

class TestHedraphone_v1:

    def test_hedraphone_v1_init(self):
        microphone = ds.microphones.Hedraphone_v1(file_path=os.path.join("tests", "_tmp", "test_hedraphone_v1_init.wav"), sample_rate=44100)
        assert isinstance(microphone, ds.microphones.Hedraphone_v1)
        assert isinstance(microphone, ds.microphones.MicrophoneArray)
        assert microphone.sample_rate == 44100

class TestHedraphone_v2:

    def test_hedraphone_v2_init(self):
        microphone = ds.microphones.Hedraphone_v2(file_path=os.path.join("tests", "_tmp", "test_hedraphone_v2_init.wav"), sample_rate=44100)
        assert isinstance(microphone, ds.microphones.Hedraphone_v2)
        assert isinstance(microphone, ds.microphones.MicrophoneArray)
        assert microphone.sample_rate == 44100