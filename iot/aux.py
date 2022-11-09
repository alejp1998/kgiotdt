# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Alejandro Jarabo
# Created Date: 2022-09-19
# Contact : ale.jarabo.penas@ericsson.com
# version ='1.0'
# ---------------------------------------------------------------------------
""" Auxiliary Variables/Functions/Imports
Module defining auxiliary elements for the IoT Devices module.
"""
# ---------------------------------------------------------------------------
# Imports
from threading import Thread
from paho.mqtt import client as mqtt_client

from json import dumps
from numpy import random
import numpy as np

from datetime import datetime, timedelta
import time, re, uuid

from colorama import Fore, Style
from builtins import print as prnt
# ---------------------------------------------------------------------------

###########################
######## VARIABLES ########
###########################

# Numpy random generator
rng = random.default_rng()

# Root topics for publishing
prodline_root   = 'productionline'
safetyenv_root  = 'safetyenvironmental'

# Other variables
arrow_str       = '     |------> '
arrow_str2      = '     |          |---> '

#########################
######## CLASSES ########
#########################

# Class providing ground truth for ambient variables such as temperature, pressure...
class GroundTruth(Thread) :
    # Initialization
    def __init__(self,ground_truth_vars):
        Thread.__init__(self)
        self.ground_truth_vars = {}
        # Initialize each variable
        for name, params in ground_truth_vars.items() :
            mu, sigma = params
            self.ground_truth_vars[name] = sample_normal_mod(mu,sigma)
    
    # New ground truth series samples
    def update_ground_truth_vars(self):
        for name, last_value in self.ground_truth_vars.items():
            self.ground_truth_vars[name] = get_new_sample(last_value,sigma=0.002)
    
    # Get ground truth var current value
    def get(self,var):
        return self.ground_truth_vars[var]

    # Thread execution
    def run(self):
        while True : 
            # Update ground truth series values and sleep for 100ms
            self.update_ground_truth_vars()
            time.sleep(0.1)

###########################
######## FUNCTIONS ########
###########################

# Get new random sample of time series based on last one
def get_new_sample(last_sample,sigma=0.002):
    return last_sample*rng.normal(1,sigma)

# Get new sample of sine wave
def get_sine_sample(offset,amp,T,phi):
    t = time.perf_counter()
    return get_new_sample(offset + amp*np.sin((2*np.pi/T)*t + phi),sigma=0.01)

# Flip a coin (returns True with prob = prob)
def coin(prob=0.5) :
    return rng.uniform() < prob

# Generate data from a normal distribution between a min and a maximum value
def sample_normal_mod(mu,sigma=0.1,modifier=0.0) :
    # Apply modification factor to values
    mu += mu*modifier
    sigma += sigma*modifier
    th = [mu - sigma, mu + sigma] # threshold within 1 STD

    # Generate random value within thresholds
    val = rng.normal(mu,sigma)
    if val > th[0] and val < th[1] : return val
    if val < th[0] : return th[0]
    else: return th[1]

# Generate robot data
def gen_robot_data(offset,A,T,phi,actuator_status):
    return {
        'joint1': {
            'x_position' : get_sine_sample(offset,A,T,phi),
            'y_position' : get_sine_sample(offset+1,A*2,T/2,phi),  
            'z_position' : get_sine_sample(offset-1,A/2,T*2,phi),
            'roll_orientation' : get_sine_sample(offset+np.pi/2,A,T,phi), 
            'pitch_orientation' : get_sine_sample(offset+6*np.pi/4,A*2,T/2,phi), 
            'yaw_orientation' : get_sine_sample(offset-6*np.pi/4,A/2,T*2,phi)
        },
        'joint2': {
            'x_position' : get_sine_sample(offset,A,T,phi),
            'y_position' : get_sine_sample(offset+2,A*2,T/2,phi),  
            'z_position' : get_sine_sample(offset-2,A/2,T*2,phi),
            'roll_orientation' : get_sine_sample(offset+np.pi/2,A,T,phi), 
            'pitch_orientation' : get_sine_sample(offset+3*np.pi/4,A*2,T/2,phi), 
            'yaw_orientation' : get_sine_sample(offset-3*np.pi/4,A/2,T*2,phi)
        },
        'joint3': {
            'x_position' : get_sine_sample(offset,A,T,phi),
            'y_position' : get_sine_sample(offset+3,A*2,T/2,phi),  
            'z_position' : get_sine_sample(offset-3,A/2,T*2,phi),
            'roll_orientation' : get_sine_sample(offset+np.pi/2,A,T,phi), 
            'pitch_orientation' : get_sine_sample(offset+2*np.pi/4,A*2,T/2,phi), 
            'yaw_orientation' : get_sine_sample(offset-2*np.pi/4,A/2,T*2,phi)
        },
        'actuator': {
            'x_position' : get_sine_sample(offset,A,T,phi),
            'y_position' : get_sine_sample(offset+4,A*2,T/2,phi),  
            'z_position' : get_sine_sample(offset-4,A/2,T*2,phi),
            'roll_orientation' : get_sine_sample(offset+np.pi/2,A,T,phi), 
            'pitch_orientation' : get_sine_sample(offset+1*np.pi/4,A*2,T/2,phi), 
            'yaw_orientation' : get_sine_sample(offset-1*np.pi/4,A/2,T*2,phi),
            'actuator_status' : actuator_status
        }
    }

# Generate header data
def fill_header_data(device_name,topic,uuid):
    return {
        'name' : device_name,
        'topic' : topic,
        'uuid' : uuid,
        'timestamp' : datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    }

# Fill module uuids
def fill_module_uuids(data,module_uuids):
    i = 0
    dev_module_uuids = []
    for mname in data :
        data[mname]['uuid'] = module_uuids[i]
        dev_module_uuids.append(module_uuids[i])
        i += 1
    return data, dev_module_uuids

# Print device data
def print_device_data(timestamp,data) :
    print(arrow_str + f'[timer]',kind='')
    print(arrow_str2 + f'(timestamp)<datetime>={timestamp}',kind='')
    for mname in data :
        print(arrow_str + f'[{mname}]',kind='')
        for mproperty in data[mname] :
            print(arrow_str2 + f'({mproperty})={data[mname][mproperty]}',kind='')

# Colored prints
def print(text,kind='') :
    prnt(cprint_dict[kind] + str(text) + Style.RESET_ALL)


##############################
######## DICTIONARIES ########
##############################

# Colored prints
cprint_dict = {
    'info':     Fore.WHITE,
    'success' : Fore.GREEN,
    'fail':     Fore.RED,
    'summary':  Fore.MAGENTA,
    'debug':    Fore.BLUE,
    '':         Fore.YELLOW 
}
