'''
This is for importing and testing already collected data (e.g. Physionet data)
'''
#Backend imports
import os
os.chdir("/Users/marcusvincentbellajaro/Documents/Coding_Projects/PulseOx")
import data_aquisition as daq
import spo2_calculation
import neurokit_peak_detection
import numpy as np
import pandas as pd
import time
import threading
import matplotlib.pyplot as plt
#Frontend imports
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Line, Color

T = 10 # time in seconds that each calc is based on
color_warning = (254/255,61/255,96/255)
color_good = (12/255,234/255,194/255,1)
R_values = []
# load a subject (1-22 should work)
daq.load_subject(5)

def back_end(self):
    #intializing plotting variables

    # while there is data left to be read, read it
    if (daq.curr_index != len(daq.r_data)):
        self.ids.process_data.disabled = True
        r_segment, ir_segment = daq.get_data(T)  # get 10 seconds of data
        # run peak detection on the IR segment
        peak_locs = neurokit_peak_detection.get_peak_locs(ir_segment)[1].get("PPG_Peaks") # the stuff at the end here is just because the thing that is returned has a bunch of info we don't care about right now
        #print(peak_locs)
        HR = (len(peak_locs)-1)/T*60
        print(f"HR: {HR}") # convert the number of peaks detected and the time overwhich they were collected into beats per minute
        ACR, DCR, ACIR, DCIR, R, spo2 = spo2_calculation.calc_spo2(r_segment, ir_segment, peak_locs)

        self.ids.HR_data.text = f'{HR} bmp' # updating HR on GUI
        self.ids.spO2_data.text = f'{spo2} %' # updating spo2 on GUI

        # Changing color based on HR and SpO2 values (danger levels)
        self.ids.HR_data.color = color_warning if (HR > 100 or HR < 60) else color_good
        self.ids.HR_title.color = self.ids.HR_data.color

        self.ids.spO2_data.color = color_warning if (spo2 < 92) else color_good
        self.ids.spO2_title.color = self.ids.spO2_data.color
        
        #Getting the data points in 10 sec interval
        plotting_points = [
            (1000*(x/(daq.f_s*T)), #Calculating time stamp of data and scaling it to fit window
             250*((r_segment[x]-min(r_segment))/(max(r_segment)-min(r_segment))) #Scaling PPG data to fit window
             ) 
             for x in range(len(r_segment))
            ]
        
        #Removing old graph and replacing it with new one
        self.ids.box.canvas.remove(self.line)
        self.ids.box.canvas.add(Color(83/255, 214/255, 237/255))
        self.line = Line(points=plotting_points, width=2)
        self.ids.box.canvas.add(self.line)
        

        R_values.append(R)
    else: # Once data ends, stops scheduled loop and renables button
        self.ids.process_data.disabled = False
        self.timer.cancel()
    
    R_start = R_values[:2]
    R_end = R_values[-2:]
    R_start = sum(R_start)/2
    R_end = sum(R_end)/2
    print(f"R_start: {R_start}\nR_end: {R_end}")

Window.size = (500,700)
Builder.load_file('pulse_ox.kv')

class PulseOxLayout(Widget):
    # Starts scheduled loop that updates labels every 0.1 seconds
    def record_data(self):
        self.timer = Clock.schedule_interval(self.update_label, 0.1)
    
    def update_label(self,*args):
        back_end(self)
    
    def __init__(self, **kwargs):
        super(PulseOxLayout, self).__init__(**kwargs)

        # Creating the line that will act as the PPG graph
        self.line = Line(points=[], width=2)
        self.ids.box.canvas.add(self.line)

class PulseOx(App):
    def build(self):
        return PulseOxLayout()

if __name__ == '__main__':
    PulseOx().run()
