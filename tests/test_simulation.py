import pytest
import sys
import os
import numpy as np
from scipy.spatial.transform import Rotation

import dynamic_sound as ds


@pytest.fixture
def simulation_empty():
    return ds.Simulation()

@pytest.fixture
def simulation_base():
    sim = ds.Simulation(temperature=25, pressure=0.98, relative_humidity=32)
    sim.add_microphone(
        path=ds.Path([
            #time,  x,   y,   z,   qw,  qx,  qy,  qz
            [0.5,   0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0],
            [0.51,   0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0]]),
        microphone=ds.microphones.Microphone(file_path=os.path.join("tests", "_tmp", "simulation_base_microphone.wav"))
    )
    sim.add_source(
        path=ds.Path([
            #time,  x,   y,     z,   qw,  qx,  qy,  qz
            [0.0,   3.0, +20.0, 1.0, 1.0, 0.0, 0.0, 0.0],
            [1.0,   3.0, -20.0, 1.0, 1.0, 0.0, 0.0, 0.0]
        ]),
        source=ds.sources.SineWave(frequency=2_000, amplitude=1.0)
    )
    return sim



class TestSimulationApi:
    def test_simulation_empty(self, simulation_empty):
        assert isinstance(simulation_empty, ds.Simulation)
        sim = simulation_empty
        assert sim.air.temperature == 20
        assert sim.air.pressure == 1
        assert sim.air.relative_humidity == 50
        assert len(sim._microphones) == 0
        assert len(sim._sources) == 0

    def test_simulation_base(self, simulation_base):
        assert isinstance(simulation_base, ds.Simulation)
        sim = simulation_base
        assert sim.air.temperature == 25
        assert sim.air.pressure == 0.98
        assert sim.air.relative_humidity == 32
        assert len(sim._microphones) == 1
        assert len(sim._sources) == 1
    
    def test_simulation_add_microphone(self, simulation_empty):
        sim = simulation_empty
        assert len(sim._microphones) == 0
        sim.add_microphone(
            path=ds.Path([
                [0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0]]),
            microphone=ds.microphones.Hedraphone_v1(file_path=os.path.join("tests", "_tmp", "test_simulation_add_microphone.wav"), sample_rate=44100)
        )
        assert len(sim._microphones) == 1
    
    def test_simulation_remove_microphones(self, simulation_base):
        sim = simulation_base
        assert len(sim._microphones) == 1
        sim.remove_microphones()
        assert len(sim._microphones) == 0
    
    def test_simulation_add_source(self, simulation_empty):
        sim = simulation_empty
        assert len(sim._sources) == 0
        sim.add_source(
            path=ds.Path([
                [0.0, 3.0, +20.0, 1.0, 1.0, 0.0, 0.0, 0.0],
                [1.0, 3.0, -20.0, 1.0, 1.0, 0.0, 0.0, 0.0]
            ]),
            source=ds.sources.SineWave(frequency=2_000, amplitude=1.0)
        )
        assert len(sim._sources) == 1
    
    def test_simulation_remove_sources(self, simulation_base):
        sim = simulation_base
        assert len(sim._sources) == 1
        sim.remove_sources()
        assert len(sim._sources) == 0

    def test_compute_emission(self, simulation_base):
        sim = simulation_base
        source_path = sim._sources[0][0]
        position_receiver = np.array([0.0, 0.0, 1.0])
        time_receiver = 0.5
        time_emission, position_emission, rotation_emission = sim._compute_emission(position_receiver, time_receiver, source_path)
        assert isinstance(time_emission, float)
        assert isinstance(position_emission, np.ndarray)
        assert isinstance(rotation_emission, Rotation)

    def test_simulation_incidence_angle_rad(self):
        p1 = [0, 0, 0]
        p2 = [1, 0, 0]
        r1 = Rotation.from_euler('z', 90, degrees=True)
        angle_rad = ds.Simulation._incidence_angle_rad(p1, p2, r1)
        assert isinstance(angle_rad, float)

    def test_simulation_run(self, simulation_base):
        sim = simulation_base
        sim.run()
        assert os.path.exists(os.path.join("tests", "_tmp", "simulation_base_microphone.wav"))
