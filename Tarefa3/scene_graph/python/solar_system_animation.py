import math
from engine import Engine
from transform import Transform

class SolarSystemAnimation(Engine):
    def __init__(self, earth_orbit_transform, moon_orbit_transform, earth_spin_transform, sun_spin_transform):
        self.earth_orbit_transform = earth_orbit_transform
        self.moon_orbit_transform = moon_orbit_transform
        self.earth_spin_transform = earth_spin_transform
        self.sun_spin_transform = sun_spin_transform

    def Update(self, time):
        self.earth_orbit_transform.LoadIdentity()
        self.moon_orbit_transform.LoadIdentity()
        self.earth_spin_transform.LoadIdentity()
        self.sun_spin_transform.LoadIdentity()

        earth_orbit_speed = 0.5
        moon_orbit_speed = 3.0
        earth_spin_speed = 2.0
        sun_spin_speed = 0.2

        earth_orbit_angle_rad = time * earth_orbit_speed
        moon_orbit_angle_rad = time * moon_orbit_speed
        earth_spin_angle_rad = time * earth_spin_speed
        sun_spin_angle_rad = time * sun_spin_speed
        
        self.earth_orbit_transform.Rotate(math.degrees(earth_orbit_angle_rad), 0, 0, 1)
        self.moon_orbit_transform.Rotate(math.degrees(moon_orbit_angle_rad), 0, 0, 1)
        self.earth_spin_transform.Rotate(math.degrees(earth_spin_angle_rad), 0, 0, 1)
        self.sun_spin_transform.Rotate(math.degrees(sun_spin_angle_rad), 0, 0, 1)