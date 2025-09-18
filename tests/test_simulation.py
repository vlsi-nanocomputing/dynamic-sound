from dynamic_sound import Simulation, CustomArray, get_sinewave


def test_simulation():
    # simulation parameters
    sample_rate = 8_000
    sim = Simulation(sample_rate=sample_rate, time_start=0.0, time_duration=8.0)

    # microphones
    custom_array = CustomArray(num_external_mics=5, radius_mics=0.020, radius_pcb=0.035, sideboard_angle=63.43, spacing=0.035, rnd_angle=None, rnd_position=None)
    sim.add_microphones(microphones=custom_array.get_microphones().T, path=(
        (0.0, (0, 0, 1.0)),
        (8.0, (0, 0, 1.0))
    ))

    # sound source
    samples = get_sinewave(frequency=2_000, duration=10, sample_rate=sample_rate)
    sim.add_source(samples=samples, path=(
        (0.0, (3, 30, 1)),
        (8.0, (3, -30, 1))
    ))

    # run simulation
    sim.run(output_filename="tests/_tmp/output.wav")
    

