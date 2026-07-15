import pytest
import os
import numpy as np

import dynamic_sound as ds


class TestSineGenerator:

    def test_sine_generator(self):
        signal, metadata = ds.generators.sine_generator(f=440, fs=48000, amplitude=1.0, length="period", filename=None, type=None)
        assert isinstance(signal, np.ndarray)
        assert isinstance(metadata, dict)
        assert np.max(np.abs(signal)) <= 1.0 + 1e-12

class TestNoiseGenerator:

    def test_noise_generator(self):
        signal, metadata = ds.generators.noise_generator(fs=48000, amplitude=1.0, length=int(1.0 * 48000), filename=None, type=None)
        assert isinstance(signal, np.ndarray)
        assert isinstance(metadata, dict)
        assert signal.shape[0] == 48000
        assert np.max(np.abs(signal)) <= 1.0 + 1e-12