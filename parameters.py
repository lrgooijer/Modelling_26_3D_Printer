
   # TODO : Come up with better estimates for these
    #        as these are placeholders

class Parameters:
    fric_lx = 0.2 # Bearing friction linear x-direction [Ns/m]
    fric_ly = 0.2 # Bearing friction linear y-direction [Ns/m]
    fric_roll = 0.1 #Bearing friction rolling [Nms/rad]
    r_m = 0.05 # Motor pulley radius [m]
    m = 0.100 # Tool Head mass [kg]
    Jmotor = 0.500 # Motor Rotor inertia [kgm^2]
    Km = 2 # Motor torque / back-EMF constant [Nm/a]
    Lm = 1 # Motor inductance [H]
    R_motor = 4 # Motor resistance [ohm]
    Cap_n = 100 # Nozzle Capacitance [F]
    C_tn = 1200 # Nozzle thermal capacity [J/K]
    R_tn = 1000 # Nozzle thermal Resistance [K/W]
    R_n = 4 # Nozzle resistance [ohm]
    t_env = 20 # Celcius
    L_n = 4 # Nozzle inductance [H]

class Bounds:
    xmax = 0.30 # Maximum x to bound printer to print plate
    ymax = 0.30 # Maximum y to bound printer to print plate


class Intial:
    x0 = Bounds.xmax / 2
    y0 = Bounds.ymax / 2