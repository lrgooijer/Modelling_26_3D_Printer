import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np


# Material properties and heat transfer coefficients for standard PLA filament
# Collected from https://www.simplify3d.com/resources/materials-guide/properties-table/
# and https://www.makeitfrom.com/material-properties/Polylactic-Acid-PLA-Polylactide
# and estimated guesses.
c_filament = 1800  # Specific heat capacity of filament (J/kg·k)
rho = 1240  # Density of filament (kg/m³)
h_air = 25 # w/(m²·k)
h_plate = 250 # w/(m²·k)
t_air = 20 # Celsius
t_plate = 60 # Celsius
w = 0.01 # m
norm_pc = rho * c_filament
delta_x = 0.01 # m 
k = 0.13
T_NOZZLE : int = 220 #Celsius
THRESHOLD_EQUIL = 1e-3 # Threshold for DTdt to call it an equillibrium
K_STEPS = 1000 # keep this high,since there is a Equillibrium brake


I_MAX = 101 # Maximum number of sections to print/ Length of filament on the spool


def heat_exchange_per_unit_volume(T:np.ndarray,i:int ,n_printed:int) -> float:
    """
    This function calculates the heat exchange of a cell. 
    Based on the Heat exchange with the surroundings and the internal conduction of the filament.
    """
    conduction_coff : float = (k/(norm_pc*delta_x**2))
    air_coff : float = (h_air/norm_pc)
    plate_coff : float = (h_plate/norm_pc)
    if n_printed == I_MAX:
        sur_heat_exc = air_coff * (3/w)*(t_air-T[i])+plate_coff*(1/w)*(t_plate-T[i])
        con_heat_exc = conduction_coff * ((T[(i+1) % I_MAX] - T[i])+(T[i-1]-T[i]))
    elif n_printed == 1 : # Only one printed, no neighbours
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

    tot_heat_exc : float = sur_heat_exc + con_heat_exc
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
    k_steps = K_STEPS
    dt : int = 1
    T_outcomes =np.full((k_steps, I_MAX), np.nan)

    for time_step in range(k_steps):
        if n_printed < I_MAX:
            T[n_printed]= T_NOZZLE
            n_printed += 1
        dTdt = compute_temperature_change(T, n_printed)
        T[:n_printed] += dt * dTdt
        T_outcomes[time_step] = T
        if n_printed == I_MAX and (abs(dTdt) < THRESHOLD_EQUIL).all():
            print(f"Equillibrium threshold reached at time step {time_step}.")
            break
    n_passed = time_step + 1
    T_outcomes = T_outcomes[:n_passed]
    distance = np.arange(I_MAX) * delta_x
    time = np.arange(n_passed) * dt
    return distance, time, T_outcomes

if __name__ == "__main__":
    distance, time, T_outcomes = simulate_printing()
    fig, ax = plt.subplots()
    line, = ax.plot([], [], "r-")
    ax.set_ylabel("Temperature[°C]")
    ax.set_xlabel("Printed distance[m]")
    ax.set_ylim(0,T_NOZZLE+10)
    ax.set_xlim(0, I_MAX * delta_x)
    ax.grid(True)
    title = ax.set_title('Temperature Distribution Over Time')

    def update(frame):
        line.set_data(distance, T_outcomes[frame])
        #bar.set_data(T_outcomes[frame][np.newaxis, :])
        title.set_text(f'Temperature Distribution at Time {frame} s')
        return line, title #, bar


simulation = animation.FuncAnimation(fig, update, frames=range(len(time)), interval=100)   
plt.show()



