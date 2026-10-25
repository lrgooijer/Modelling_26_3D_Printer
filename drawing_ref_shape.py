import numpy as np
from main_simulation import system
from parameters import Parameters as p

Jtot = p.Jmotor +(1/2)*p.m*(p.r_m**2)
b_plus = p.fric_roll + ((p.r_m**2)/4) * (p.fric_lx + p.fric_ly) 
b_min = ((p.r_m**2)/4) * (p.fric_lx - p.fric_ly)

def reference_ellipse(t, x_c, y_c, a, b, w):
    
    x_ref = x_c + a * np.cos(w*t)
    d_x_ref = -a * w * np.sin(w*t) 
    dd_x_ref =  -a * w**2 * np.cos(w*t) 
    ddd_x_ref =  a * w**3 * np.sin(w*t)

    y_ref = y_c + b * np.sin(w*t)
    d_y_ref = b * w * np.cos(w*t) 
    dd_y_ref =  -b * w**2 * np.sin(w*t) 
    ddd_y_ref =  -b * w**3 * np.cos(w*t)

    return (x_ref,d_x_ref,dd_x_ref,ddd_x_ref), (y_ref,d_y_ref,dd_y_ref, ddd_y_ref)  


def draw_ellipse():

    #TODO define fric_lz
    b_z = p.fric_roll +((p.r_m**2)*fric_lz)/2
    u_x = (u_ml + u_mr)/2
    u_y = (u_ml - u_mr)/2

    u_ml = u_x + u_y
    u_mr = u_x - u_y
    return ...
