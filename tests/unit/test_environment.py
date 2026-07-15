import pytest

import dynamic_sound as ds


class TestAir:

    def test_air_init(self):
        air = ds.environment.Air(25, 0.98, 32)
        assert air.temperature == 25
        assert air.pressure == 0.98
        assert air.relative_humidity == 32
    
    def test_air_set(self):
        air = ds.environment.Air(25, 0.98, 32)
        air.set(temperature=30)
        assert air.temperature == 30
        assert air.pressure == 0.98
        assert air.relative_humidity == 32
        
        air.set(pressure=1.0)
        assert air.temperature == 30
        assert air.pressure == 1.0
        assert air.relative_humidity == 32
        
        air.set(relative_humidity=50)
        assert air.temperature == 30
        assert air.pressure == 1.0
        assert air.relative_humidity == 50
