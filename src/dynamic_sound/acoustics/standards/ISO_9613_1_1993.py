import numpy as np

SOUND_SPEED = 343.2  # [m/s] = 1235.52 km/h
REFERENCE_TEMPERATURE = 293.15  # [K] = 20.0 °C
REFERENCE_PRESSURE = 101.325  # [kPa] = 1 atm
TRIPLE_TEMPERATURE = 273.16  # [K] = 0.01 °C


def sound_speed(temperature, reference_temperature=REFERENCE_TEMPERATURE):
    return SOUND_SPEED * np.sqrt(temperature / reference_temperature)

def saturation_pressure(temperature, reference_pressure=REFERENCE_PRESSURE, triple_temperature=TRIPLE_TEMPERATURE):  # (ISO 9613-1: B.2, B.3)
    return reference_pressure * 10.0**(-6.8346 * (triple_temperature / temperature)**(1.261) + 4.6151)

def molar_concentration_water_vapour(relative_humidity, saturation_pressure, pressure): # # (ISO 9613-1: B.1)
    return relative_humidity * saturation_pressure / pressure

def relaxation_frequency_oxygen(pressure, h, reference_pressure=REFERENCE_PRESSURE):  # (ISO 9613-1: 3)
    return pressure / reference_pressure * (24.0 + 4.04 * 10.0**4.0 * h * (0.02 + h) / (0.391 + h))

def relaxation_frequency_nitrogen(pressure, temperature, h, reference_temperature=REFERENCE_TEMPERATURE, reference_pressure=REFERENCE_PRESSURE):  # (ISO 9613-1: 4)
    return pressure / reference_pressure * (temperature / reference_temperature)**(-0.5) * (9.0 + 280.0 * h * np.exp(-4.170 * ((temperature / reference_temperature)**(-1.0 / 3.0) - 1.0)))

def attenuation_coefficients(frequency, temperature, relative_humidity, pressure, reference_temperature=REFERENCE_TEMPERATURE, reference_pressure=REFERENCE_PRESSURE, triple_temperature=TRIPLE_TEMPERATURE):  # (ISO 9613-1: 5)   
    Psat = saturation_pressure(temperature=temperature, reference_pressure=reference_pressure, triple_temperature=triple_temperature)
    h = molar_concentration_water_vapour(relative_humidity=relative_humidity, saturation_pressure=Psat, pressure=pressure)
    frO = relaxation_frequency_oxygen(pressure=pressure, h=h, reference_pressure=reference_pressure)
    frN = relaxation_frequency_nitrogen(pressure, temperature, h, reference_temperature=reference_temperature, reference_pressure=reference_pressure)

    return 8.686 * frequency**2 * (
        (1.84e-11 * (pressure / reference_pressure)**(-1.0) * (temperature / reference_temperature)**0.5) +
        (temperature / reference_temperature)**(-5.0/2.0) * (
            0.01275 * np.exp(-2239.1 / temperature) / (frO + (frequency**2 / frO)) +
            0.1068 * np.exp(-3352.0 / temperature) / (frN + (frequency**2 / frN)) 
        )
    )
