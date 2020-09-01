#%%
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 14:18:08 2019

@author: Alec Eickbusch
"""

import numpy as np
import qutip as qt
from helper_functions import alpha_from_epsilon

#%%
def gaussian_wave(sigma, chop=4):
    ts = np.linspace(-chop/2*sigma, chop/2*sigma, chop*sigma)
    P = np.exp(-ts**2 / (2.0 * sigma**2))
    ofs = P[0]
    return (P - ofs) / (1 - ofs)
#rotate qubit angle theta around axis phi on the bloch sphere
def rotate(theta, phi=0, sigma=8, chop=6, dt=1):
    wave = gaussian_wave(sigma=sigma, chop=chop)
    energy = np.trapz(wave, dx = dt)
    amp_pi = np.pi / (2*energy)
    wave = (1 + 0j)*wave
    return (theta/np.pi) * amp_pi * np.exp(1j*phi) * wave

#displace cavity by an amount alpha
def disp(alpha, sigma=8, chop=6, dt=1):
    wave = gaussian_wave(sigma=sigma, chop=chop)
    energy = np.trapz(wave, dx = dt)
    wave = (1 + 0j)*wave
    return (np.abs(alpha)/energy) * np.exp(1j*(np.pi/2.0 + np.angle(alpha))) * wave

def CD(beta, alpha0 = 60, chi=2*np.pi*1e-3*0.03, sigma=4, chop=4, sigma_q=4, chop_q=4, buffer_time=0):
    #will have to think about CDs where it's too to have any zero time given beta bare
    
    #beta = 2*chi*int(alpha)

    #intermederiate pulse used to find the energy in the displacements
    def beta_bare(sigma, chop):
        epsilon_bare = np.concatenate([
        disp(alpha0, sigma, chop),
        disp(-1*alpha0, sigma, chop)])

        alpha_bare = alpha_from_epsilon(epsilon_bare)
        return 2*2*chi*np.sum(alpha_bare) #extra factor of 2 for negative part
    while beta_bare(sigma, chop) > beta:
        sigma = int(sigma - 1)
    return beta_bare(sigma, chop), sigma, chop

        

    total_time = np.abs(beta/(2*alpha0*chi))
    zero_time = int(round(total_time/2))
    alpha0 = np.abs(beta/(2*2*zero_time*chi)) #a slight readjustment due to the rounding
    alpha_angle = np.angle(beta) + np.pi/2.0 #todo: is it + or - pi/2?
    alpha0 = alpha0*np.exp(1j*alpha_angle)
    
    epsilon = np.concatenate([
    disp(alpha0, sigma, chop),
    np.zeros(zero_time),
    disp(-1*alpha0, sigma, chop),
    np.zeros(buffer_time + sigma_q*chop_q + buffer_time),
    disp(-1*alpha0, sigma, chop),
    np.zeros(zero_time),
    disp(alpha0, sigma, chop)])

    alpha = alpha_from_epsilon(epsilon)
    beta = 2*chi*np.sum(np.abs(alpha))

    Omega = np.concatenate([
        np.zeros(zero_time + 2*sigma*chop + buffer_time),
        rotate(np.pi,sigma=sigma_q,chop=chop_q),
        np.zeros(zero_time + 2*sigma*chop + buffer_time)
    ])

    return epsilon, Omega, beta, alpha
# %%

# %%