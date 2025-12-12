
class Air:
    def __init__(self, temperature, pressure, relative_humidity):
        self.temperature = temperature
        self.pressure = pressure
        self.relative_humidity = relative_humidity
    
    def set(self, temperature=None, pressure=None, relative_humidity=None):
        self.temperature = temperature if temperature is not None else self.temperature
        self.pressure = pressure if pressure is not None else self.pressure
        self.relative_humidity = relative_humidity if relative_humidity is not None else self.relative_humidity
