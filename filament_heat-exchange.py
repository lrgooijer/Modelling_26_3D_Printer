import matplotlib.pyplot as plt
import numpy as np

c_filament = 1000  # Specific heat capacity of filament (J/kg·k)
rho = 1000  # Density of filament (kg/m³)
h_air = 1000
h_plate = 4000
t_air = 20 # Celsius
t_plate = 80 # Celsius
w = 0.01 # m
norm_pc = rho * c_filament
delta_x = 0.01 # m 
k = 0.9

I_MAX = 100


def heat_exchange_per_unit_volume(t:float,i:int ,n_printed:int) -> float:
    """
    This function calculates the heat exchange of a cell. 
    Based on the Heat exchange with the surroundings and the internal conduction of the filament.
    """

    if i==0 or i==I_MAX-1:
        sur_heat_exc = (h_air/norm_pc) * (3/w+1/delta_x)*(t_air-t(i))+(h_plate/norm_pc)*(1/w)*(t_plate-t(i))
        if i==0:
            con_heat_exc= (k*w**2/norm_pc) * (t(i+1) - t(i))
        if i==I_MAX-1:
            con_heat_exc = (k*w**2/norm_pc) * (t(i-1) - t(i))

    sur_heat_exc = (h_air/norm_pc) * (3/w)*(t_air-t(i))+(h_plate/norm_pc)*(1/w)*(t_plate-t(i))
    con_heat_exc = (k*w**2/norm_pc) * ((t(i+1) - t(i))+(t(i-1)-t(i)))

    tot_heat_exc = sur_heat_exc + con_heat_exc
    return tot_heat_exc

def compute_temperature_change(T:float, n_printed:int) -> np.ndarray:
    i_sections : list = range(n_printed)
    dTdt : list = np.zeros(n_printed)
    for i in i_sections:
         dTdt[i] = heat_exchange_per_unit_volume(T[i], i, n_printed)
    return dTdt

def simulate_printing()-> list[float]:
    """
    Calculate the change in Temprature
    """
    T = np.full(I_MAX, np.nan) 
    n_printed = 0
    timesteps : list = np.linspace(1,100,100)
    dt : int = 1
    t_n  = 100 #Celsius

    for time_step in timesteps:
        T[n_printed]= t_n
        n_printed += 1
        dTdt = compute_temperature_change(T, n_printed)
        T[:n_printed] += dt * dTdt

        


