import os
import numpy as np
import dynamic_sound as ds

res_path = os.path.join("examples", "resources")
microphone_sample_rate = 100
source_sample_rate = 100


def test_air_coefficients():

    temp = [-20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    freq = np.array([50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000])
    humidity = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    pressure = 101.325
    distance = 1000
    
    for temp_i in temp:
        print("----------------------------------")
        print(f"Temperature: {temp_i} °C")
        temp_i = temp_i+273.15
        print("Humidity (%) |", end="")

        for hum_i in humidity:
            print(f"{hum_i:10.0f} |", end="")
            
        for freq_i in freq:
            print(f"\n{freq_i:12.0f} |", end="")
            for hum_i in humidity:
                val = ds.acoustics.standards.ISO_9613_1_1993.attenuation_coefficients(frequency=freq_i, temperature=temp_i, pressure=pressure, relative_humidity=hum_i)
                print(f"{val*distance:10.2e} |", end="")
        
        print()

if __name__ == "__main__":
    test_air_coefficients()
