
import os
import numpy as np
from scipy.special import erf
from scipy.integrate import quad_vec
import matplotlib.pyplot as plt
from scipy.special import exp1


def concat(dh):    
    dh = [np.fliplr(dh), dh]
    dh = np.concatenate(dh, axis=1)
    dh = [np.flipud(dh), dh]
    dh = np.concatenate(dh, axis=0)
    return dh

def mirror(u, y_axis=True):

    u = [-1*np.fliplr(u), u]
    u = np.concatenate(u, axis=1)
    u = [np.flipud(u), u]
    u = np.concatenate(u, axis=0)
    u = np.fliplr(u)
    return u

def compute_integral(alpha, beta):
    def func(tau):
        return erf(alpha / np.sqrt(tau)) * erf(beta / np.sqrt(tau))
    
    result, error = quad_vec(func, 0, 1.0)
    return result

def compute_mounding_grid(Lx, Ly, N, l, a, t, b, w, k, sy, h0):

    if N is None:
        N = 20

    v = 4*t*k*b/sy
    x = np.linspace(0, Lx, N)
    y = np.linspace(0, Ly, N)
    x, y = np.meshgrid(x, y)

    p1 = (l+x)/np.sqrt(v)
    p2 = (a+y)/np.sqrt(v)
    s1 = compute_integral(p1, p2)

    p1 = (l+x)/np.sqrt(v)
    p2 = (a-y)/np.sqrt(v)
    s2 = compute_integral(p1, p2)

    p1 = (l-x)/np.sqrt(v)
    p2 = (a+y)/np.sqrt(v)
    s3 = compute_integral(p1, p2)

    p1 = (l-x)/np.sqrt(v)
    p2 = (a-y)/np.sqrt(v)
    s4 = compute_integral(p1, p2)

    s = s1+s2+s3+s4

    v1 =k*b/sy
    dh = (w/(2*k)) * (v1 * t) * s

    dh = concat(dh)
    gw_grad = mirror(gw_grad, y_axis=True)
    dh = h0 + dh 

def compute_recharge_rate(x,y,t,del_h, spread_area, k,b,sy):

    v = 4*t*k*b/sy
    l = np.sqrt(spread_area)
    a = l
    p1 = (l+x)/np.sqrt(v)
    p2 = (a+y)/np.sqrt(v)
    s1 = compute_integral(p1, p2)

    p1 = (l+x)/np.sqrt(v)
    p2 = (a-y)/np.sqrt(v)
    s2 = compute_integral(p1, p2)

    p1 = (l-x)/np.sqrt(v)
    p2 = (a+y)/np.sqrt(v)
    s3 = compute_integral(p1, p2)

    p1 = (l-x)/np.sqrt(v)
    p2 = (a-y)/np.sqrt(v)
    s4 = compute_integral(p1, p2)

    s = s1+s2+s3+s4

    h2 = np.power(del_h, 2)
    v1 =k*b/sy

    recharge_rate = 2 * k * h2/(v1*t*s)    
    return recharge_rate

def theis_drawdown_or_Q(Q_or_dh, T, S, r, t, compute_Q=True):
    """
    Computes the drawdown (dh) or pumping rate (Q) in a confined aquifer using 
    the Theis (Transient) solution.

    The Theis equation is given by: s = (Q / (4 * pi * T)) * W(u)

    Parameters:
    -----------
    Q : float
        Pumping rate (Volume/Time, e.g., m^3/day).
    T : float
        Aquifer Transmissivity (Area/Time, e.g., m^2/day).
    S : float
        Aquifer Storativity (dimensionless).
    r : float
        Radial distance from the pumping well (Length, e.g., m).
    t : float
        Time since pumping started (Time, e.g., day).

    Returns:
    --------
    float
        The calculated drawdown (s) at distance 'r' and time 't' (Length, e.g., m).
        Returns 0 if time 't' is zero to avoid division by zero.
    """
    # Ensure all inputs are positive floats
    if T <= 0 or S <= 0 or r <= 0:
        raise ValueError("Q, T, S, and r must be positive.")

    # Handle the t=0 case, as drawdown is zero before pumping starts
    if t <= 0:
        return 0.0

    # 1. Calculate the 'u' parameter (Dimensionless time/distance parameter)
    # u = (r^2 * S) / (4 * T * t)
    # 
    try:
        u = (r**2 * S) / (4 * T * t)
    except Exception as e:
        print(f"Error calculating u: {e}")
        return 0.0

    # 2. Calculate the Well Function W(u)
    # The Well Function W(u) is mathematically equivalent to the Exponential Integral E1(u)
    # W(u) = E1(u) = integral from u to infinity of (e^-y / y) dy
    try:
        # exp1 is the scipy function for the Exponential Integral E1(u)
        W_u = exp1(u)
    except Exception as e:
        # Fallback for extreme u values, although exp1 is robust
        print(f"Error calculating W(u): {e}. Returning 0.")
        return 0.0

    # 3. Calculate Drawdown (s)
    # s = (Q / (4 * pi * T)) * W(u)
    if compute_Q:
        drawdown = Q_or_dh
        Q = (drawdown/W_u) * (4 * np.pi * T)
        return Q

    else:
        Q = Q_or_dh
        drawdown= (Q / (4 * np.pi * T)) * W_u
        return drawdown
