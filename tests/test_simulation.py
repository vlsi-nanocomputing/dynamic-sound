from dynamic_sound import Simulation, get_sinewave, HedraPhone_v2, get_white_noise
from dynamic_sound import molar_concentration_water_vapour, air_absorption_coefficients, nitrogen_relaxation_contribution, oxygen_relaxation_contribution, saturation_pressure, classical_contribution
import numpy as np

def test_environment():
    temp = [-20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    freq = np.array([50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000])
    humidity = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]


    f = np.logspace(1, 6, 500)
    T = 20+273.15
    h_rel = 50
    pa = 101.325
    h = molar_concentration_water_vapour(relative_humidity=h_rel, saturation_pressure=saturation_pressure(temperature=T), pressure=pa)
    alpha_coeff = air_absorption_coefficients(f=f, T=T, pa=pa, hr=h_rel)
    alpha_O = oxygen_relaxation_contribution(frequency=f, temperature=T, pressure=pa, h=h)
    alpha_N = nitrogen_relaxation_contribution(frequency=f, pressure=pa, temperature=T, h=h)
    alpha_C = classical_contribution(frequency=f, pressure=pa, temperature=T)

    distance = 1000
    alpha_coeff = 10**(-alpha_coeff * distance / 20)

    for temp_i in temp:
        print("----------------------------------")
        print(f"Temperature: {temp_i} °C")
        temp_i = temp_i+273.15
        print("Humidity (%) |", end="")

        for hum_i in humidity:
            print(f"{hum_i:10.2f} |", end="")
            
        for freq_i in freq:
            print(f"\n{freq_i:12.0f} |", end="")
            for hum_i in humidity:
                val = air_absorption_coefficients(f=freq_i, T=temp_i, pa=101.325, hr=hum_i)
                print(f"{val*1000:10.2e} |", end="")
        
        print()


def test_simulation():
    # simulation parameters
    sample_rate = 8_000
    sim = Simulation(sample_rate=sample_rate, time_start=0.0, time_duration=8.0)
    sim.set_environment(temperature=20, pressure=1, relative_humidity=50)

    # microphones
    # sim.add_microphones(microphones=HedraPhone_v2.get_microphones(), path=(
    #     (0.0, (0, 0, 1.0)),
    #     (8.0, (0, 0, 1.0))
    # ))
    sim.add_microphones((0.0, 0.0, 0.0), path=(
        (0.0, (0, 0, 1.0)),
        (8.0, (0, 0, 1.0))
    ))

    # sound source
    #samples = get_sinewave(frequency=2_000, duration=10, sample_rate=sample_rate)
    samples = get_white_noise(duration=10, sample_rate=sample_rate)
    sim.add_source(samples=samples, path=(
        (0.0, (3, 20, 1)),
        (8.0, (3, -20, 1))
    ))

    # image source
    samples = get_sinewave(frequency=2_000, duration=10, sample_rate=sample_rate)
    sim.add_source(samples=samples, path=(
        (0.0, (3, 20, -1)),
        (8.0, (3, -20, -1))
    ))

    # run simulation
    sim.run(output_filename="tests/_tmp/output.wav")

