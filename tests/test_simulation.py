import dynamic_sound as ds

microphone_sample_rate = 100
source_sample_rate = 100

def test_simulation():
    sim = ds.Simulation(temperature=20, pressure=1, relative_humidity=50)
    mic_path = ds.Path(file="tests/resources/paths/camera_path.csv")
    sim.add_microphone(path=mic_path, microphone=ds.microphones.MicrophoneArray(positions=[
                     [0.0, 0.0, 0.0,        0.0, 0.0, 0.0, 0.0]
            ], file_path="tests/_tmp/airsim_path_drone_sound.wav", sample_rate=microphone_sample_rate)
    )

    drone_sound = ds.sources.AudioFile(filename=r"tests/resources/sounds/flying_drone.wav", sample_rate=source_sample_rate, gain_db=10.0, loop=True)
    drone_path = ds.Path(file="tests/resources/paths/drone_path.csv")
    sim.add_source(path=drone_path, source=drone_sound)
    drone_path.positions[:,3] = -drone_path.positions[:,3]
    sim.add_source(path=drone_path, source=drone_sound)
    sim.run()


def test_simulation_2():
    sim = ds.Simulation(temperature=20, pressure=1, relative_humidity=50)
    sim.add_microphone(path=ds.Path([
            [0.0,     0.0, 2.0, 1.0,        1.0, 0.0, 0.0, 0.0],
            [30.0,    0.0, 2.0, 1.0,        1.0, 0.0, 0.0, 0.0]
        ]), microphone=ds.microphones.MicrophoneArray(positions=[
                     [0.0, 0.0, 0.0,        1.0, 0.0, 0.0, 0.0]
            ], file_path="tests/_tmp/path_with_interpolation_drone_sound.wav", sample_rate=microphone_sample_rate)
    )

    drone_sound = ds.sources.AudioFile(filename=r"tests/resources/sounds/flying_drone.wav", sample_rate=source_sample_rate, gain_db=10.0, loop=True)
    path = ds.Path([
        [ 0.0,      0.0,   0.0,   0.0,     0.0, 0.0, 0.0, 1.0],            # Start on ground, level
        [ 5.0,      0.0,   0.0,   0.0,     0.0, 0.0, 0.0, 1.0],            # Hover on ground (idle until 5s)
        [ 8.0,     10.0,   0.0,  10.0,     0.0, 0.0, 0.0, 1.0],            # Begin takeoff and small forward move, level
        [12.0,     40.0,   0.0,  30.0,     0.0, 0.0, 0.2588, 0.9659],      # Ascend and accelerate forward, slight yaw (~30°)
        [15.0,     80.0,  20.0,  60.0,     0.0, 0.0, 0.5,    0.8660],      # Continue climb + forward, yaw ~60°
        [16.0,    120.0,  60.0,  80.0,     0.0, 0.0, 0.7660, 0.6428],      # Faster forward leg, yaw ~100°
        [18.0,    140.0,  90.0, 100.0,     0.2588,0.2588,0.2588,0.9239],  # Banked/curved turn (mixed roll/pitch)
        [21.0,    160.0, 120.0,  90.0,     0.0, 0.0, 0.9397, 0.3420],      # Turning further (yaw ~140°), slight descent
        [24.0,    150.0, 100.0,  70.0,     0.0, 0.0, 0.9848,-0.1736],      # Return-leg / heading reversal, yaw ~200°
        [27.0,    170.0,  60.0,  60.0,     0.0, 0.0, 0.9848, 0.1736],      # Move back toward side, yaw ~160°
        [30.0,    200.0,  40.0,  80.0,     0.0, 0.0, 0.0,    1.0],        # Move away again, level flight (still in air)
    ])
    path.interpolate_path(50)
    sim.add_source(path=path, source=drone_sound)
    path.positions[:,3] = -path.positions[:,3]
    sim.add_source(path=path, source=drone_sound)
    sim.run()


def test_simulation_3():
    sim = ds.Simulation(temperature=20, pressure=1, relative_humidity=50)
    sim.add_microphone(path=ds.Path([
            [0.0, 0.0, 0.0, 1.0,       1.0, 0.0, 0.0, 0.0],
            [8.0, 0.0, 0.0, 1.0,       1.0, 0.0, 0.0, 0.0]
        ]), microphone=ds.microphones.Hedraphone_v1(file_path="tests/_tmp/white_noise_and_refletion.wav", sample_rate=microphone_sample_rate)
    )

    white_noise = ds.sources.WhiteNoise(duration=8.0, sample_rate=source_sample_rate, amplitude=1.0)
    sim.add_source(path=ds.Path([
            [0.0, 3.0, 20.0, 1.0,      1.0, 0.0, 0.0, 0.0],
            [8.0, 3.0, -20.0, 1.0,     1.0, 0.0, 0.0, 0.0]
        ]), source=white_noise
    )
    sim.add_source(path=ds.Path([
            [0.0, 3.0, 20.0, -1.0,     1.0, 0.0, 0.0, 0.0],
            [8.0, 3.0, -20.0, -1.0,    1.0, 0.0, 0.0, 0.0]
        ]), source=white_noise
    )
    sim.run()


def test_simulation_4():
    sim = ds.Simulation(temperature=20, pressure=1, relative_humidity=50)
    sim.air.set(temperature=35, pressure=1.5, relative_humidity=90)
    sim.add_microphone(path=ds.Path([
            [0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0],
            [8.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0]
        ]), microphone=ds.microphones.Hedraphone_v2(file_path="tests/_tmp/sinewave_and_reflection.wav", sample_rate=microphone_sample_rate, rnd_angle=0.01, rnd_position=0.001)
    )

    sin_signal = ds.sources.SineWave(frequency=2_000, sample_rate=source_sample_rate, amplitude=1.0)
    sim.add_source(path=ds.Path([
            [0.0, 3.0, 20.0, 1.0, 1.0, 0.0, 0.0, 0.0],
            [8.0, 3.0, -20.0, 1.0, 1.0, 0.0, 0.0, 0.0]
        ]), source=sin_signal
    )
    sim.add_source(path=ds.Path([
            [0.0, 3.0, 20.0, -1.0, 1.0, 0.0, 0.0, 0.0],
            [8.0, 3.0, -20.0, -1.0, 1.0, 0.0, 0.0, 0.0]
        ]), source=sin_signal
    )
    sim.run()

def test_path():
    path = ds.Path([
        [0.0, 3.0, 20.0, 1.0, 1.0, 0.0, 0.0, 0.0],
        [8.0, 3.0, -20.0, 1.0, 1.0, 0.0, 0.0, 0.0]
    ])
    path.save_path("tests/_tmp/test_path.path")

    path2 = ds.Path()
    path2.load_path("tests/_tmp/test_path.path")

    path2.plot_path_3d(show=False)
    path2.plot_quaternion_directions(show=False)

    position, rotation = path2.get_position(-1)
    assert position is None
    assert rotation is None


if __name__ == "__main__":
    test_simulation()
