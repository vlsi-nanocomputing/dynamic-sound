import numpy as np

def sound_attenuation(distance: float) -> float:
    return 1 / (2 * np.pi * distance**2)

SOUNDSPEED = 343.2
"""
Speed of sound = 343.2 m/s at 20 degrees Celsius.
"""

REFERENCE_TEMPERATURE = 293.15
"""
Reference temperature = 293.15 K (20 degrees Celsius).
"""

REFERENCE_PRESSURE = 101.325
"""
International Standard Atmosphere 101.325 kPa (1 atm).
"""

TRIPLE_TEMPERATURE = 273.16
""".
Triple point isotherm temperature = 273.16 K (0.01 degrees Celsius).
"""

def soundspeed(temperature, reference_temperature=REFERENCE_TEMPERATURE):
    return SOUNDSPEED * np.sqrt(temperature / reference_temperature)

def saturation_pressure(temperature, reference_pressure=REFERENCE_PRESSURE, triple_temperature=TRIPLE_TEMPERATURE):
    return reference_pressure * 10.0**(-6.8346 * (triple_temperature / temperature)**(1.261) + 4.6151)

def molar_concentration_water_vapour(relative_humidity, saturation_pressure, pressure):
    return relative_humidity * saturation_pressure / pressure

def relaxation_frequency_oxygen(pressure, h, reference_pressure=REFERENCE_PRESSURE):
    return pressure / reference_pressure * (24.0 + 4.04 * 10.0**4.0 * h * (0.02 + h) / (0.391 + h))

def relaxation_frequency_nitrogen(pressure, temperature, h, reference_pressure=REFERENCE_PRESSURE, reference_temperature=REFERENCE_TEMPERATURE):
    return pressure / reference_pressure * (temperature / reference_temperature)**(-0.5) * (9.0 + 280.0 * h * np.exp(-4.170 * ((temperature / reference_temperature)**(-1.0 / 3.0) - 1.0)))

def classical_contribution(frequency, pressure, temperature, reference_pressure=REFERENCE_PRESSURE, reference_temperature=REFERENCE_TEMPERATURE):
    return 8.686 * frequency**2 * (1.84e-11 * (pressure / reference_pressure)**-1 * (temperature / reference_temperature)**(1/2))

def oxygen_relaxation_contribution(frequency, temperature, pressure, h, reference_pressure=REFERENCE_PRESSURE, reference_temperature=REFERENCE_TEMPERATURE):
    frO = relaxation_frequency_oxygen(pressure, h, reference_pressure)
    return 8.686 * frequency**2 * ((temperature / reference_temperature)**(-5/2) * 0.01275 * np.exp(-2239.1 / temperature) / (frO + (frequency**2 / frO)))

def nitrogen_relaxation_contribution(frequency, pressure, temperature, h, reference_pressure=REFERENCE_PRESSURE, reference_temperature=REFERENCE_TEMPERATURE):
    frN = (pressure / reference_pressure) * (temperature / reference_temperature)**-0.5 * (9 + 280 * h * np.exp(-4.170 * ((temperature / reference_temperature)**(-1.0/3.0) - 1)))
    return 8.686 * frequency**2 * ((temperature / reference_temperature)**(-5/2) * 0.1068 * np.exp(-3352.0 / temperature) / (frN + (frequency**2 / frN)))

def air_absorption_coefficients(f: float,
                                T:float=20+273.15,    # Ambient air temperature in degrees Celsius
                                pa:float=101.325,  # Ambient atmospheric pressure in kPa
                                hr:float=50) -> np.ndarray:  # Relative humidity (0-100)
    
    T0 = REFERENCE_TEMPERATURE  # Reference air temperature in Kelvins (20 degrees Celsius)
    pr = REFERENCE_PRESSURE  # Reference ambient athmospheric pressure in kPa (1 atm)
    
    # Conversion of humidity data to molar concentration of water vapour (ISO 9613-1: Annex B)
    T01 = 273.16    # Triple point isotherm temperature in Kelvins (+0.01 degrees Celsius)
    C = -6.8346 * (T01 / T)**1.261 + 4.6151  # (ISO 9613-1: B.3)
    Psat = pr * 10**C  # (ISO 9613-1: B.2)
    h = hr * Psat / pa # h=hr*(Psat/pr)/(pa/pr) --> h=hr*(Psat/pa)  # (ISO 9613-1: B.1)

    frO = (pa / pr) * (24.0 + 4.04e4 * h * (0.02 + h) / (0.391 + h))  # (ISO 9613-1: 3)
    frN = (pa / pr) * (T / T0)**-0.5 * (9 + 280 * h * np.exp(-4.170 * ((T / T0)**(-1.0/3.0) - 1)))  # (ISO 9613-1: 4)

    alpha_coeff = 8.686 * f**2 * (  # sound attenuation coefficients in decibels per metre (ISO 9613-1: 5)
        (1.84e-11 * (pa / pr)**-1 * (T / T0)**0.5) +
        (T / T0)**(-5.0/2.0) * (
            0.01275 * np.exp(-2239.1 / T) / (frO + (f**2 / frO)) +
            0.1068 * np.exp(-3352.0 / T) / (frN + (f**2 / frN)) 
        )
    )
    return alpha_coeff

def precompute_pseud_A(frequencies, sample_rate):
    # Compute air absorption filter
    w = 2 * np.pi * frequencies / (sample_rate / 2)
    # Filter order - air absorption
    L_air = 10
    # Matrix A
    A = np.zeros((len(w),int(L_air/2 + 1)))
    A[:,0] = 1
    for i in range(len(w)):
        for j in range(1,int(L_air/2 + 1)):
            A[i,j] = 2 * np.cos(w[i] * j)
    return np.linalg.inv(A.T.dot(A)).dot(A.T)


def compute_air_absorption_filter(pseud_A, airAbsorptionCoefficients, distance: float, numtaps: int) -> np.ndarray:
    filt_coeffs = np.empty(numtaps, np.float64)
    alpha = 10 ** (-airAbsorptionCoefficients * distance / 20)     # Convert coeffs in dB to linear scale
    filt_coeffs[int((numtaps+1)/2)-1:] = pseud_A.dot(alpha)
    filt_coeffs[0:int((numtaps+1)/2)-1] = np.flip(filt_coeffs[int((numtaps+1)/2):])
    return filt_coeffs
