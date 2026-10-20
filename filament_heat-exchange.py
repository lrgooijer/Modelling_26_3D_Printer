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

#TODO get better estimate for filament properties, and the heat transfer coefficients.

I_MAX = 101


def heat_exchange_per_unit_volume(T:np.ndarray,i:int ,n_printed:int) -> float:
    """
    This function calculates the heat exchange of a cell. 
    Based on the Heat exchange with the surroundings and the internal conduction of the filament.
    """
    conduction_coff = (k*w**2/norm_pc) # TODO pretty sure this is wrong
    air_coff = (h_air/norm_pc)
    plate_coff = (h_plate/norm_pc)
    if n_printed == 1 : # Only one printed, no neighbours
        sur_heat_exc = air_coff * (3/w+1/delta_x)*(t_air-T[i])+plate_coff*(1/w)*(t_plate-T[i])
        con_heat_exc = 0 # nothing to conduct to
    elif i==0: # First section    
        sur_heat_exc = air_coff * (3/w+1/delta_x)*(t_air-T[i])+plate_coff*(1/w)*(t_plate-T[i])
        con_heat_exc= conduction_coff * (T[i+1] - T[i])
    elif i==n_printed-1: # Last section
        sur_heat_exc = air_coff * (3/w+1/delta_x)*(t_air-T[i])+plate_coff*(1/w)*(t_plate-T[i])
        con_heat_exc = conduction_coff * (T[i-1] - T[i])
    else:
        sur_heat_exc = air_coff * (3/w)*(t_air-T[i])+plate_coff*(1/w)*(t_plate-T[i])
        con_heat_exc = conduction_coff * ((T[i+1] - T[i])+(T[i-1]-T[i]))

    tot_heat_exc = sur_heat_exc + con_heat_exc
    return tot_heat_exc

def compute_temperature_change(T:np.ndarray, n_printed:int) -> np.ndarray:
    """
    Calculate the change in Temprature of the printed sections
    """
    i_sections : list = range(n_printed)
    dTdt : np.ndarray = np.zeros(n_printed)
    for i in i_sections:
         dTdt[i] = heat_exchange_per_unit_volume(T, i, n_printed)
    return dTdt

def simulate_printing()-> list[float]:
    """
    This runs over the timesteps computing the heat and 
    "printing" a new cell each timestep. 
    """
    T = np.full(I_MAX, np.nan) 
    n_printed = 0
    n_steps = 100
    dt : int = 1
    t_n : int = 100 #Celsius
    T_outcomes =np.full((n_steps, I_MAX), np.nan)

    for time_step in range(n_steps):
        T[n_printed]= t_n
        n_printed += 1 # TODO maybe try to decouple printing for timesteps, to make it fancier
        dTdt = compute_temperature_change(T, n_printed)
        T[:n_printed] += dt * dTdt
        T_outcomes[time_step] = T
    return T_outcomes

if __name__ == "__main__":
    T_outcomes = simulate_printing()
    print(T_outcomes)

#mesh = plt.pcolormesh()





