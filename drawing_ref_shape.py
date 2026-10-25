import numpy as np
from main_simulation import system
from parameters import Parameters as p


Jtot = p.Jmotor +(1/2)*p.m*(p.r_m**2)
b_plus = p.fric_roll + ((p.r_m**2)/4) * (p.fric_lx + p.fric_ly) 
b_min = ((p.r_m**2)/4) * (p.fric_lx - p.fric_ly)

b_x = b_plus +  b_min
b_y = b_plus -  b_min

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


def input_u_z(t, d_z_ref, dd_z_ref, ddd_z_ref, b_z):
    input_u_z = (p.Lm * Jtot/ (p.r_m* p.Km)) *ddd_z_ref +((p.Lm * b_z + p.R_motor * Jtot)/p.r_m*p.Km)*dd_z_ref + (p.R_motor * b_z / (p.r_m * p.Km) + p.Km / p.r_m) * d_z_ref
    return input_u_z

def draw_ellipse(t, x_c, y_c, a, b, w, u_n = 0): # TODO u_n=0 is placeholder

    (x_ref,d_x_ref,dd_x_ref,ddd_x_ref) = reference_ellipse(t, x_c, y_c, a, b, w)
    (y_ref,d_y_ref,dd_y_ref, ddd_y_ref) = reference_ellipse(t, x_c, y_c, a, b, w)

    u_x = input_u_z(d_x_ref,dd_x_ref,ddd_x_ref)
    u_y = input_u_z(d_y_ref,dd_y_ref, ddd_y_ref)

    u_ml = u_x + u_y
    u_mr = u_x - u_y

    u_inputs_ellipse = np.array([u_ml. u_mr, u_n])
    return u_inputs_ellipse
