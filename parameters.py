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
    heater_u_max = 24 # Maximum volatge heater [V]
    heater_u_nom = 13.66 # Steady state voltage heate [V] #TODO add calculation to report
    t_nozzle_printing = 220 # Nozzle temperature when printing


class Bounds:
    xmax = 0.30 # Maximum x to bound printer to print plate
    ymax = 0.30 # Maximum y to bound printer to print plate


class Intial:
    x_center = Bounds.xmax / 2
    y_center = Bounds.ymax / 2


class Q14:
    q = 0 # Printing state
    time_loop = 200
    a  = 0.03
    b = 0.06

class Clover:
    q = 0 # Printing state
    time_loop = 200
    a  = 0.1
    b = 0.3

class Square:
    side_length = 0.12
    x_start = 0.09
    y_start = 0.09

class Events:
    S_max = 0.25 # Filament length until new is needed [m]
    t_C  = 1000 # Test with lower value,time for this colour
    w_wipe = 2*np.pi /2 # Wipe Frequency
    u_wipe = 1 # Determines magnitude of the y-wipe
    Kd_brake = 0.02 # 
    dt_wipe = 20 # [s]
    dt_load = 30 # [s]
    T_low  = 150 # Celcius
    T_high = 220 # Celcius
    cap_dtheta = 0.01 # Threshold stopping
    u_corner = 1 # Constant voltage to drive head to corner
    threshold_bound = 0.01 # # Distance from axis to count as having left it [m]
    threshold_saved_loc = 1e-3  # Arrival tolerance at the location
    Kp_pos  = 1# Proportional gain to position
    Kd_pos  = 1# Derivative gain
    threshold_bound_theta = 0.01 # Condition that the Motors must be almost stopped in the corners
    threshold_bound_omega = 0.01 # Condition that the Motors must be almost stopped in the corners


