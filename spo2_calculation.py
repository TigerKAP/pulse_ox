# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 22:38:56 2024

@author: kaiab

implementation of spo2 algorithm in python
requires IR and R signal and peaks returned by a peak detection algorithm
"""
import sys
from statistics import mean
from decimal import Decimal

def calc_spo2(r_segment, ir_segment, peak_locs):
    # the x coordinate of the IR peaks found by the peak detection algorithm.
    # also the x coordinate of the R peaks since signals are in phase
    IR_signal = ir_segment
    R_signal = r_segment
    signal_peak_locs = peak_locs
    signal_valley_locs = [None] * len(signal_peak_locs)  # Create an empty list of the same length

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
    # ensure both are the same length
    signal_peak_locs = signal_peak_locs[0:len(signal_peak_locs)-1]
    signal_valley_locs = signal_valley_locs[0:len(signal_peak_locs)]
    


          
    # initialize arrays of the same size as number of peaks to store AC and DC comps of R and IR signals
    ACRs = [0] * len(signal_peak_locs)  # Initialize ACRs with a list of zeros
    DCRs = [0] * len(signal_peak_locs)  # Initialize DCRs with a list of zeros
    ACIRs = [0] * len(signal_peak_locs)  # Initialize ACIRs with a list of zeros
    DCIRs = [0] * len(signal_peak_locs)  # Initialize DCIRs with a list of zeros

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
        ACRs[i] = ACR
        DCRs[i] = DCR
        ACIRs[i] = ACIR
        DCIRs[i] = DCIR
    
    # take averages over the values in the arrays
    
    
    ACR = mean(ACRs) #AC component of red
    DCR = mean(DCRs) #DC component of red
    ACIR = mean(ACIRs) # AC component of infrared signal
    DCIR = mean(DCIRs) # DC component of infrared signal
    """
    ACR = Decimal(sum(ACRs)) / Decimal(len(ACRs))  # AC component of red
    DCR = Decimal(sum(DCRs)) / Decimal(len(DCRs))  # DC component of red
    ACIR = Decimal(sum(ACIRs)) / Decimal(len(ACIRs))  # AC component of infrared signal
    DCIR = Decimal(sum(DCIRs)) / Decimal(len(DCIRs))  # DC component of infrared signal
    """
    
    R = (ACR/DCR)/(ACIR/DCIR) # caclculate ratio of ratios
    

    
    # apply calibration curve to ratio of ratios
    spo2 = calibration_curve(R)
    return ACR, DCR, ACIR, DCIR, R, spo2
# calibration curve from MAXIM library
def calibration_curve(R):
    ret = -45.060*R**2 + 30.354 *R + 94.845 
    ret = int(ret)
    return ret


