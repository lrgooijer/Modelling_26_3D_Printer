import numpy as np
from parameters import Parameters as p

Jtot = p.Jmotor +(1/2)*p.m*(p.r_m**2)
b_plus = p.fric_roll + ((p.r_m**2)/4) * (p.fric_lx + p.fric_ly) 
b_min = ((p.r_m**2)/4) * (p.fric_lx - p.fric_ly)

b_x = b_plus +  b_min
b_y = b_plus -  b_min

def intial_state(x_ref,y_ref):
    (x0, d_x0, dd_x0, ddd_x0) = x_ref
    (y0, d_y0, dd_y0, ddd_y0) = y_ref

    i_x0 = input_i_z(d_x0, dd_x0, b_x)
    i_y0  = input_i_z(d_y0, dd_y0, b_y)

    state0 = np.zeros(13)
    state0[0]= (x0 + y0) / p.r_m # theta_l invert the kinematics
    state0[1]= (x0 - y0) / p.r_m # theta_r invert the kinematics
    state0[2] = (d_x0 + d_y0) / p.r_m #dtheta_l
    state0[3] = (d_x0 - d_y0) / p.r_m #dtheta_r
    state0[4] = i_x0 + i_y0 #i_l
    state0[5] = i_x0 - i_y0 #i_r
    state0[6] = p.t_nozzle_printing
    return state0

def reference_clover(t, x_c, y_c, a, b, w):
    h = a/2
    x_ref     = x_c + h*( np.cos(3*w*t)+ np.cos(w*t))
    d_x_ref   =       h*(-3*w*np.sin(3*w*t)- w*np.sin(w*t))
    dd_x_ref  =       h*(-9*w**2*np.cos(3*w*t)- w**2*np.cos(w*t))
    ddd_x_ref =       h*( 27*w**3*np.sin(3*w*t)+ w**3*np.sin(w*t))

    y_ref     = y_c + h*( np.sin(3*w*t)- np.sin(w*t))
    d_y_ref   =       h*( 3*w*np.cos(3*w*t)- w*np.cos(w*t))
    dd_y_ref  =       h*(-9*w**2*np.sin(3*w*t)+ w**2*np.sin(w*t))
    ddd_y_ref =       h*(-27*w**3*np.cos(3*w*t)+ w**3*np.cos(w*t))

    return (x_ref,d_x_ref,dd_x_ref,ddd_x_ref), \
            (y_ref,d_y_ref,dd_y_ref, ddd_y_ref)



def reference_ellipse(t, x_c, y_c, a, b, c_w): 
    x_ref = x_c + a * np.cos(c_w*t)
    d_x_ref = -a * c_w * np.sin(c_w*t) 
    dd_x_ref =  -a * c_w**2 * np.cos(c_w*t) 
    ddd_x_ref =  a * c_w**3 * np.sin(c_w*t)

    y_ref = y_c + b * np.sin(c_w*t)
    d_y_ref = b * c_w * np.cos(c_w*t) 
    dd_y_ref =  -b * c_w**2 * np.sin(c_w*t) 
    ddd_y_ref =  -b * c_w**3 * np.cos(c_w*t)

    return (x_ref,d_x_ref,dd_x_ref,ddd_x_ref), (y_ref,d_y_ref,dd_y_ref, ddd_y_ref)  

def input_i_z(d_z_ref, dd_z_ref, bz):
    input_i_z = (Jtot * dd_z_ref + bz * d_z_ref) / (p.r_m * p.Km) 
    return input_i_z


def input_u_z(t, d_z_ref, dd_z_ref, ddd_z_ref, b_z):
    input_u_z = (p.Lm * Jtot/ (p.r_m* p.Km)) *ddd_z_ref +((p.Lm * b_z + p.R_motor * Jtot)/(p.r_m*p.Km))*dd_z_ref + (p.R_motor * b_z / (p.r_m * p.Km) + p.Km / p.r_m) * d_z_ref
    return input_u_z

def draw_ellipse( t ,x_c, y_c, a, b, w, u_n = p.heater_u_nom):
    (x_ref,d_x_ref,dd_x_ref,ddd_x_ref), (y_ref,d_y_ref,dd_y_ref, ddd_y_ref) = reference_ellipse(t, x_c, y_c, a, b, w)

    u_x = input_u_z(t, d_x_ref,dd_x_ref,ddd_x_ref, b_x)
    u_y = input_u_z(t, d_y_ref,dd_y_ref, ddd_y_ref, b_y)

    u_ml = u_x + u_y
    u_mr = u_x - u_y

    u_inputs_ellipse = np.array([u_ml, u_mr, u_n])
    return u_inputs_ellipse

def draw_clover( t ,x_c, y_c, a, b, c_w, u_n = p.heater_u_nom):
    (x_ref,d_x_ref,dd_x_ref,ddd_x_ref), (y_ref,d_y_ref,dd_y_ref, ddd_y_ref) = reference_clover(t, x_c, y_c, a, b, c_w)
    
    u_x = input_u_z(t, d_x_ref,dd_x_ref,ddd_x_ref, b_x)
    u_y = input_u_z(t, d_y_ref,dd_y_ref, ddd_y_ref, b_y)

    u_ml = u_x + u_y
    u_mr = u_x - u_y

    u_inputs_clover_h = np.array([u_ml, u_mr, u_n])
    return u_inputs_clover_h


