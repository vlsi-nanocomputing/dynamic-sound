import pytest
import sys
import os
import numpy as np

import dynamic_sound as ds



class TestDoppler:

    def test_doppler_frequency(self):
        f0 = 1000
        c = 343
        v_source = 10
        v_receiver = 5
        f_expected = f0 * (c + v_receiver) / (c + v_source)
        f1 = ds.acoustics.doppler.frequency(
            frequency=f0,
            velocity_source=v_source,
            velocity_receiver=v_receiver,
            soundspeed=c
        )
        assert f1 == pytest.approx(f_expected, rel=1e-12)
    
    def test_doppler_velocity(self):
        f1 = 1000
        f2 = 1014.4927536231884
        c = 343
        v_expected = c * (f2 - f1) / (f2 + f1)
        v = ds.acoustics.doppler.velocity(f1=f1, f2=f2, c=c)
        assert v == pytest.approx(v_expected, rel=1e-12)


class TestAttenuations:

    def test_geometric_attenuation(self):
        distance = 10
        expected_attenuation = 1 / distance
        attenuation = ds.acoustics.attenuations.geometric(distance)
        assert attenuation == pytest.approx(expected_attenuation, rel=1e-12)
    
    def test_geometric_attenuation_zero_distance(self):
        distance = 0
        expected_attenuation = 1.0
        attenuation = ds.acoustics.attenuations.geometric(distance)
        assert attenuation == pytest.approx(expected_attenuation, rel=1e-12)
    
    def test_material_reflection(self):
        coeff = 0.5
        expected_reflection = 1.0
        reflection = ds.acoustics.attenuations.material_reflection(coeff)
        assert reflection == pytest.approx(expected_reflection, rel=1e-12)

    @pytest.mark.parametrize("directivity_pattern, name, expected_attenuation", [
        (ds.acoustics.attenuations.DirectivityType.OMNIDIRECTIONAL, "omnidirectional", [1.0                             for _ in np.linspace(0, 2 * np.pi, 360)]),
        (ds.acoustics.attenuations.DirectivityType.SUBCARDIOID,     "subcardioid",     [0.75 + 0.25 * np.cos(x)         for x in np.linspace(0, 2 * np.pi, 360)]),
        (ds.acoustics.attenuations.DirectivityType.CARDIOID,        "cardioid",        [0.5 + 0.5 * np.cos(x)           for x in np.linspace(0, 2 * np.pi, 360)]),
        (ds.acoustics.attenuations.DirectivityType.SUPERCARDIOID,   "supercardioid",   [np.abs(0.25 + 0.75 * np.cos(x)) for x in np.linspace(0, 2 * np.pi, 360)]),
        (ds.acoustics.attenuations.DirectivityType.HYPERCARDBOID,   "hypercardioid",   [np.abs(0.37 + 0.63 * np.cos(x)) for x in np.linspace(0, 2 * np.pi, 360)]),
        (ds.acoustics.attenuations.DirectivityType.FIGURE8,         "figure8",         [np.abs(np.cos(x))               for x in np.linspace(0, 2 * np.pi, 360)]),
        (ds.acoustics.attenuations.DirectivityType.QUADCOPTER,      "quadcopter",      [10**((-0.0011 * x**2 + 0.194 * np.abs(x) - 8.55) / 20) for x in ((np.rad2deg(np.linspace(0, 2 * np.pi, 360)) % 180) - 90) ]),    
    ])
    def test_directivity_attenuation(self, directivity_pattern, name,expected_attenuation):
        assert ds.acoustics.attenuations.DirectivityType.name(directivity_pattern) == name
        attenuation = [ds.acoustics.attenuations.directivity(x, directivity_pattern) for x in np.linspace(0, 2 * np.pi, 360)]
        assert attenuation == pytest.approx(expected_attenuation, rel=1e-12)
    
    def test_directivity_invalid(self):
        with pytest.raises(ValueError):
            ds.acoustics.attenuations.DirectivityType.name(0)
        with pytest.raises(ValueError):
            ds.acoustics.attenuations.DirectivityType.name(999)
        with pytest.raises(ValueError):
            ds.acoustics.attenuations.directivity(0, 0)
        with pytest.raises(ValueError):
            ds.acoustics.attenuations.directivity(0, 999)

        
