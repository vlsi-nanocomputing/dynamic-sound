import pytest
import os
import numpy as np

import dynamic_sound as ds


class TestSineWave:

    def test_init(self):
        source = ds.sources.SineWave(frequency=440)
        assert isinstance(source, ds.sources.Source)
        assert source.frequency == 440
        assert source.amplitude == 1.0
        assert source.directivity == ds.acoustics.attenuations.DirectivityType.OMNIDIRECTIONAL
        source = ds.sources.SineWave(frequency=1000, amplitude=0.5, directivity=ds.acoustics.attenuations.DirectivityType.CARDIOID)
        assert source.frequency == 1000
        assert source.amplitude == 0.5
        assert source.directivity == ds.acoustics.attenuations.DirectivityType.CARDIOID
    
    def test_get_sample(self):
        source = ds.sources.SineWave(frequency=440, amplitude=1.0)
        sample = source.get_sample(0.0)
        assert sample == pytest.approx(0.0, abs=1e-12)
        sample = source.get_sample(1/440)
        assert sample == pytest.approx(0.0, abs=1e-12)
        sample = source.get_sample(1/880)
        assert sample == pytest.approx(0.0, abs=1e-12)
        sample = source.get_sample(1/1760)
        assert sample == pytest.approx(1.0, abs=1e-12)
        sample = source.get_sample(1/3520)
        assert sample == pytest.approx(np.sqrt(2)/2, abs=1e-12)

class TestWhiteNoise:

    def test_init(self):
        source = ds.sources.WhiteNoise(duration=1.0)
        assert isinstance(source, ds.sources.Source)
        assert source.sample_rate == 48000
        assert source.signal.shape[0] == 48000
        assert np.max(np.abs(source.signal)) <= 1.0+1e-12
        source = ds.sources.WhiteNoise(duration=2.0, sample_rate=44100, amplitude=0.5)
        assert source.sample_rate == 44100
        assert source.signal.shape[0] == 88200
        assert np.max(np.abs(source.signal)) <= 0.5+1e-12
    
    def test_get_sample(self):
        source = ds.sources.WhiteNoise(duration=1.0)
        sample = source.get_sample(0.0)
        assert np.abs(sample) <= 1.0+1e-12
        sample = source.get_sample(0.5)
        assert np.abs(sample) <= 1.0+1e-12
        with pytest.raises(IndexError) as e_info:
            sample = source.get_sample(1.0)
    
class TestAudioFile:
    
    def test_init(self):
        source = ds.sources.AudioFile(filename=os.path.join("tests", "res", "audio", "sine_440_1s.wav"))
        assert isinstance(source, ds.sources.Source)
        assert source.sample_rate == 48000
        assert source.signal.shape[0] == 48000
        assert np.max(np.abs(source.signal)) == pytest.approx(1.0, abs=1e-12)
        source = ds.sources.AudioFile(filename="tests/res/audio/sine_440_1s.wav", gain_db=-6.020599913279624)
        assert np.max(np.abs(source.signal)) == pytest.approx(0.5, abs=1e-12)

    def test_get_sample_none(self):
        source = ds.sources.AudioFile(filename=os.path.join("tests", "res", "audio", "sine_440_1s.wav"), interpolation=ds.sources.InterpolationType.NONE)
        sample = source.get_sample(0.0)
        assert sample == pytest.approx(0.0, abs=1e-12)
    
    def test_get_sample_linear(self):
        source = ds.sources.AudioFile(filename=os.path.join("tests", "res", "audio", "sine_440_1s.wav"), interpolation=ds.sources.InterpolationType.LINEAR)
        sample = source.get_sample(0.0)
        assert sample == pytest.approx(0.0, abs=1e-12)

    def test_get_sample_sinc(self):
        source = ds.sources.AudioFile(filename=os.path.join("tests", "res", "audio", "sine_440_1s.wav"), interpolation=ds.sources.InterpolationType.SINC)
        sample = source.get_sample(0.0)
        assert sample == pytest.approx(0.0, abs=1e-12)
    
    def test_get_sample_interpolation_not_implemented(self):
        source = ds.sources.AudioFile(filename=os.path.join("tests", "res", "audio", "sine_440_1s.wav"), interpolation=999)
        with pytest.raises(NotImplementedError) as e_info:
            sample = source.get_sample(0.0)
    
    def test_get_sample_loop_false(self):
        source = ds.sources.AudioFile(filename=os.path.join("tests", "res", "audio", "sine_440_1s.wav"), loop=False, interpolation=ds.sources.InterpolationType.NONE)
        sample = source.get_sample(0.0)
        assert sample == pytest.approx(0.0, abs=1e-12)
        sample = source.get_sample(10.0)
        assert sample == pytest.approx(0.0, abs=1e-12)

        source = ds.sources.AudioFile(filename=os.path.join("tests", "res", "audio", "sine_440_1s.wav"), loop=False, interpolation=ds.sources.InterpolationType.LINEAR)
        sample = source.get_sample(10.0)
        assert sample == pytest.approx(0.0, abs=1e-12)

        source = ds.sources.AudioFile(filename=os.path.join("tests", "res", "audio", "sine_440_1s.wav"), loop=False, interpolation=ds.sources.InterpolationType.SINC)
        sample = source.get_sample(10.0)
        assert sample == pytest.approx(0.0, abs=1e-12)

class TestAudioSignal:
    
    def test_init(self):
        signal = np.sin(2 * np.pi * 440 * np.arange(0, 1, 1/48000))
        source = ds.sources.AudioSignal(signal=signal)
        assert isinstance(source, ds.sources.Source)
        assert source.sample_rate == 48000
        assert source.signal.shape[0] == 48000
        assert np.max(np.abs(source.signal)) <= 1.0+1e-12
        source = ds.sources.AudioSignal(signal=signal, gain_db=-6.020599913279624)
        assert np.max(np.abs(source.signal)) <= 0.5+1e-12
    
    def test_get_sample_none(self):
        signal = np.sin(2 * np.pi * 440 * np.arange(0, 1, 1/48000))
        source = ds.sources.AudioSignal(signal=signal, interpolation=ds.sources.InterpolationType.NONE)
        sample = source.get_sample(0.0)
        assert sample == pytest.approx(0.0, abs=1e-12)
    
    def test_get_sample_linear(self):
        signal = np.sin(2 * np.pi * 440 * np.arange(0, 1, 1/48000))
        source = ds.sources.AudioSignal(signal=signal, interpolation=ds.sources.InterpolationType.LINEAR)
        sample = source.get_sample(0.0)
        assert sample == pytest.approx(0.0, abs=1e-12)
    
    def test_get_sample_sinc(self):
        signal = np.sin(2 * np.pi * 440 * np.arange(0, 1, 1/48000))
        source = ds.sources.AudioSignal(signal=signal, interpolation=ds.sources.InterpolationType.SINC)
        sample = source.get_sample(0.0)
        assert sample == pytest.approx(0.0, abs=1e-12)

    def test_get_sample_interpolation_not_implemented(self):
        signal = np.sin(2 * np.pi * 440 * np.arange(0, 1, 1/48000))
        source = ds.sources.AudioSignal(signal=signal, interpolation=999)
        with pytest.raises(NotImplementedError) as e_info:
            sample = source.get_sample(0.0)
    
    def test_get_sample_loop_false(self):
        signal = np.sin(2 * np.pi * 440 * np.arange(0, 1, 1/48000))
        source = ds.sources.AudioSignal(signal=signal, loop=False, interpolation=ds.sources.InterpolationType.NONE)
        sample = source.get_sample(0.0)
        assert sample == pytest.approx(0.0, abs=1e-12)
        sample = source.get_sample(10.0)
        assert sample == pytest.approx(0.0, abs=1e-12)

        source = ds.sources.AudioSignal(signal=signal, loop=False, interpolation=ds.sources.InterpolationType.LINEAR)
        sample = source.get_sample(10.0)
        assert sample == pytest.approx(0.0, abs=1e-12)

        source = ds.sources.AudioSignal(signal=signal, loop=False, interpolation=ds.sources.InterpolationType.SINC)
        sample = source.get_sample(10.0)
        assert sample == pytest.approx(0.0, abs=1e-12)

class TestDrone:

    def test_init(self):
        source = ds.sources.Drone(filename=os.path.join("tests", "res", "audio", "sine_440_1s.wav"))
        assert isinstance(source, ds.sources.Source)
        assert source.sample_rate == 48000
        assert source.signal.shape[0] == 48000
        assert np.max(np.abs(source.signal)) <= 1.0+1e-12
        source = ds.sources.Drone(filename=os.path.join("tests", "res", "audio", "sine_440_1s.wav"), gain_db=-6.020599913279624)
        assert np.max(np.abs(source.signal)) <= 0.5+1e-12
    
    def test_get_sample_none(self):
        source = ds.sources.Drone(filename=os.path.join("tests", "res", "audio", "sine_440_1s.wav"), interpolation=ds.sources.InterpolationType.NONE)
        sample = source.get_sample(0.0)
        assert sample == pytest.approx(0.0, abs=1e-12)
    
    def test_get_sample_linear(self):
        source = ds.sources.Drone(filename=os.path.join("tests", "res", "audio", "sine_440_1s.wav"), interpolation=ds.sources.InterpolationType.LINEAR)
        sample = source.get_sample(0.0)
        assert sample == pytest.approx(0.0, abs=1e-12)
    
    def test_get_sample_sinc(self):
        source = ds.sources.Drone(filename=os.path.join("tests", "res", "audio", "sine_440_1s.wav"), interpolation=ds.sources.InterpolationType.SINC)
        sample = source.get_sample(0.0)
        assert sample == pytest.approx(0.0, abs=1e-12)

    def test_get_sample_interpolation_not_implemented(self):
        source = ds.sources.Drone(filename=os.path.join("tests", "res", "audio", "sine_440_1s.wav"), interpolation=999)
        with pytest.raises(NotImplementedError) as e_info:
            sample = source.get_sample(0.0)
    
    def test_get_sample_loop_false(self):
        source = ds.sources.Drone(filename=os.path.join("tests", "res", "audio", "sine_440_1s.wav"), loop=False, interpolation=ds.sources.InterpolationType.NONE)
        sample = source.get_sample(0.0)
        assert sample == pytest.approx(0.0, abs=1e-12)
        sample = source.get_sample(10.0)
        assert sample == pytest.approx(0.0, abs=1e-12)

        source = ds.sources.Drone(filename=os.path.join("tests", "res", "audio", "sine_440_1s.wav"), loop=False, interpolation=ds.sources.InterpolationType.LINEAR)
        sample = source.get_sample(10.0)
        assert sample == pytest.approx(0.0, abs=1e-12)

        source = ds.sources.Drone(filename=os.path.join("tests", "res", "audio", "sine_440_1s.wav"), loop=False, interpolation=ds.sources.InterpolationType.SINC)
        sample = source.get_sample(10.0)
        assert sample == pytest.approx(0.0, abs=1e-12)