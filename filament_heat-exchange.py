import matplotlib.pyplot as plt
import numpy as np

C_FILAMENT = 1000  # Specific heat capacity of filament (J/kg·K)
RHO = 1000  # Density of filament (kg/m³)
H_AIR = 1000
H_PLATE = 4000
T_AIR = 20 # Celsius
T_N  = 100 #Celsius
T_PLATE = 80 # Celsius
W = 0.01 # m
NORM_PC = RHO * C_FILAMENT
DELTA_X = 0.01 # m 
K = 0.9

def heat_exchange_per_unit_volume(t:int,t_prev, t_next, first:bool, last:bool, current:bool) -> float:
    """
    This function calculates the heat exchange of a cell. 
    Based on the Heat exchange with the surroundings and the internal conduction of the filament.
    """

    if first or last is True:
        sur_heat_exc = (H_AIR/NORM_PC) * (3/W+1/DELTA_X)*(T_AIR-t(i))+(H_PLATE/NORM_PC)*(1/W)*(T_PLATE-t(i))
        if first is True:
            con_heat_exc= (K*W**2/NORM_PC) * (t(i+1) - t(i))
        if last is True:
            con_heat_exc = (K*W**2/NORM_PC) * (t(i-1) - t(i))

    sur_heat_exc = (H_AIR/NORM_PC) * (3/W)*(T_AIR-t(i))+(H_PLATE/NORM_PC)*(1/W)*(T_PLATE-t(i))
    con_heat_exc = (K*W**2/NORM_PC) * ((t(i+1) - t(i))+(t(i-1)-t(i)))

    tot_heat_exc = sur_heat_exc + con_heat_exc
    return tot_heat_exc

def heat_calculator()-> list[float]:


    i_sections = range(100)
    section = {
        "temprature"= t,
        "temprature_prev_neighbour"= T_before,
        "temprature_next_neighbour"= T_next,
        "first_cell"=

    }

    if 
    for i in i_sections:
        heat_exchange_per_unit_volume(T, first, last, current)