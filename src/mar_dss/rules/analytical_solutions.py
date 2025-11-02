
import os
import numpy as np
from scipy.special import erf
from scipy.integrate import quad_vec
import matplotlib.pyplot as plt


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

