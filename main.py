# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 23:06:41 2024

@author: kaiab
"""
# %%imports
import os
os.chdir("C:/Users/kaiab/OneDrive/Desktop/pulse_ox")
import data_aquisition as daq
import spo2_calculation
import neurokit_peak_detection
import numpy as np
import pandas as pd
# set the working directory
T = 10 # time in seconds that each calc is based on
# %%

# load a subject (1-15 should work)
daq.load_subject(5)

# while there is data left to be read, read it
while (daq.curr_index != len(daq.r_data)):
    r_segment, ir_segment = daq.get_data(T)  # get 10 seconds of data
    # run peak detection on the IR segment
    peak_locs = neurokit_peak_detection.get_peak_locs(ir_segment)[1].get("PPG_Peaks") # the stuff at the end here is just because the thing that is returned has a bunch of info we don't care about right now
    #print(peak_locs)
    neurokit_peak_detection.plot_with_peaks(r_segment, ir_segment, peak_locs) # can also use the built in show function from the neurokit module to visualize but that only shows the peaks on the signal it ran the algo on
    print("HR:" + str((len(peak_locs)-1)/T*60)) # convert the number of peaks detected and the time overwhich they were collected into beats per minute
    ACR, DCR, ACIR, DCIR, R, spo2 = spo2_calculation.calc_spo2(r_segment, ir_segment, peak_locs)
    print(ACR)
    print(DCR)
    print(ACIR)
    print(DCIR)
    print(R)
    print(spo2)
    #print("RoR:" + str(R))

