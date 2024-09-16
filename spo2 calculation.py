# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 22:38:56 2024

@author: kaiab

implementation of spo2 algorithm in python
requires IR and R signal and peaks returned by a peak detection algorithm
"""
import sys
from statistics import mean

IR_signal = [];
R_signal = [];
# the x coordinate of the IR peaks found by the peak detection algorithm.
# also the x coordinate of the R peaks since signals are in phase
signal_peak_locs = [10,20,40,60]; 
signal_valley_locs = []


# loop through the peak locations (exclude very first in loop params)
for i in range(1, len(signal_peak_locs)):
    minval = sys.maxsize
    minval_loc = 0
    # loop through the points between two peaks and find the smallest one (valley)
    for j in range(signal_peak_locs[i-1], signal_peak_locs[i]):
        if (IR_signal[j] < minval):
            minval = IR_signal[j]
            minval_loc = j
    signal_valley_locs[i-1] = minval_loc
    
# since we have only looked for valleys between the n peaks, there will be n-1 valleys
# delete the last peak so that peaks and valleys arrays are same length
# could also delete first peak if makes more sense physiologically
del(signal_peak_locs[len(signal_peak_locs)-1])

# initialize arrays of the same size as number of peaks to store AC and DC comps of R and IR signals
ACRs = list(range(len(signal_peak_locs)))
DCRs = list(range(len(signal_peak_locs)))
ACIRs = list(range(len(signal_peak_locs)))
DCIRs = list(range(len(signal_peak_locs)))
# use peak and valley locations to obtain peak and valley heights
for i in range(len(signal_peak_locs)):
    IR_peak = IR_signal[signal_peak_locs[i]] #get IR peak height
    IR_valley = IR_signal[signal_valley_locs[i]] # get IR valley height
    ACIR = IR_peak - IR_valley # AC component is ptp
    DCIR = IR_valley # DC component is everything below the AC component (which slightly different from how a DC offset is usually defined)
    
    R_peak = R_signal[signal_peak_locs[i]] # get R peak height
    R_valley = R_signal[signal_valley_locs[i]] # get R valley height
    ACR = R_peak - R_valley # determine AC component
    DCR = R_valley # determine DC component

# take averages over the values in the arrays

mean(DCIRs)



ACR = mean(ACRs) #AC component of red
DCR = mean(DCRs) #DC component of red
ACIR = mean(ACIRs) # AC component of infrared signal
DCIR = mean(DCIRs) # DC component of infrared signal


R = (ACR/DCR)/(ACIR/DCIR) # caclculate ratio of ratios

# calibration curve from MAXIM library
def calibration_curve(R):
    ret = -45.060*R^2 + 30.354 *R + 94.845 
    ret = int(ret)
    return ret

# apply calibration curve to ratio of ratios
spo2 = calibration_curve(R)
print(spo2)





