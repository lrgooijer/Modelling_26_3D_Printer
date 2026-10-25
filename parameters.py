import numpy as np

# Estimates for parameters of the stepper motor:
# https://www.datasheetcafe.com/17hs4401s-datasheet/ 
# https://marlinfw.org/docs/features/filament_change.html 
# https://sigmanortec.ro/en/hotend-heating-cartridge-24v-40w-6x20mm 
class Parameters:
    fric_lx = 0.3 # Bearing friction linear x-direction [Ns/m]
    fric_ly = 0.3 # Bearing friction linear y-direction [Ns/m]
    fric_roll = 1e-5 #Bearing friction rolling [Nms/rad]
    r_m = 0.0065 # Motor pulley radius [m]
    m = 0.280 # Tool Head mass [kg]
    Jmotor = 5.4e-6 # Motor Rotor inertia [kgm^2]
    Km = 0.25 # Motor torque / back-EMF constant [Nm/a]
    Lm = 2.8e-3 # Motor inductance [H]
    R_motor = 1.5 # Motor resistance [ohm]
    Cap_n = 3.5e-3 # Nozzle Capacitance [F]
    C_tn = 15 # Nozzle thermal capacity [J/K]
    R_tn = 15 # Nozzle thermal Resistance [K/W]
    R_n = 14 # Nozzle resistance [ohm]
    t_env = 20 # Celcius
    L_n = 4 # Nozzle inductance [H]

class Bounds:
    xmax = 0.30 # Maximum x to bound printer to print plate
    ymax = 0.30 # Maximum y to bound printer to print plate


class Intial: # TODO kinda wack name
    x_center = Bounds.xmax / 2
    y_center = Bounds.ymax / 2


# TODO implement this in the drawing shapes
class Q14:
    q = 0 # Printing state
    time_loop = 200
    a  = 0.001
    b = 0.0001


class Heater:
    u_max = 40 #TODO
    T_low  = 30 #TODO polacholdes
    T_high =300 # TODO

class Wipe:
    x_wipe = 0.0
    y_wipe = 0.0
    a_wipe = 0.001
    b_wipe = 0.0001

class Events:
    S_max = 1 #[m]
    t_C  = 30 # Celsius
    dt_wipe = 20 # [s]
    dt_load = 30 # [s]


