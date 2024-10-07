# -*- coding: utf-8 -*-
"""
Gets data from the physionet dataset and returns it as an array
"""

import pandas as pd
import os

r_data = []
ir_data = []
f_s = 500 # sampling 
curr_index = 0

# takes i from 1 to 15 representing subject number and loads the R and IR data for that subject
def load_subject(i):
    global r_data, ir_data, current_index
    current_index = 0
    csv = pd.read_csv("./physionet_data/s" + str(i) + "_sit.csv")  
    r_data = csv.pleth_1.to_numpy()
    ir_data = csv.pleth_2.to_numpy()

# takes a time in seconds t and returns the IR and R signals for the next t seconds
def get_data(t):
    global curr_index
    num_samples = int(f_s * t)
    end = curr_index + num_samples
    if (end > len(r_data)):
        print("end of data")
        ret_r_data =  r_data[curr_index:len(r_data)]
        ret_ir_data = ir_data[curr_index:len(r_data)]
        curr_index = len(r_data)
    else:
        ret_r_data =  r_data[curr_index:end]
        ret_ir_data = ir_data[curr_index:end]
        curr_index = end
    return ret_r_data, ret_ir_data
