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
from matplotlib.backends.backend_agg import FigureCanvasAgg
#from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

T = 10 # time in seconds that each calc is based on
color_warning = (254/255,61/255,96/255)
color_good = (12/255,234/255,194/255,1)
# load a subject (1-15 should work)
daq.load_subject(5)

def back_end(self):

    # while there is data left to be read, read it
    while (daq.curr_index != len(daq.r_data)):
        r_segment, ir_segment = daq.get_data(T)  # get 10 seconds of data
        # run peak detection on the IR segment
        peak_locs = neurokit_peak_detection.get_peak_locs(ir_segment)[1].get("PPG_Peaks") # the stuff at the end here is just because the thing that is returned has a bunch of info we don't care about right now
        #print(peak_locs)
        #neurokit_peak_detection.plot_with_peaks(r_segment, ir_segment, peak_locs) # can also use the built in show function from the neurokit module to visualize but that only shows the peaks on the signal it ran the algo on
        HR = (len(peak_locs)-1)/T*60
        print(f"HR: {HR}") # convert the number of peaks detected and the time overwhich they were collected into beats per minute
        ACR, DCR, ACIR, DCIR, R, spo2 = spo2_calculation.calc_spo2(r_segment, ir_segment, peak_locs)
        self.ids.HR_data.text = f'{HR} bmp'
        self.ids.spO2_data.text = f'{spo2} %'
        if (HR > 100 or HR < 60):
            self.ids.HR_data.color = color_warning
            self.ids.HR_title.color = color_warning
        else:
            self.ids.HR_data.color = color_good
            self.ids.HR_title.color = color_good

        if (spo2 < 92):
            self.ids.spO2_data.color = color_warning
            self.ids.spO2_title.color = color_warning
        else:
            self.ids.spO2_data.color = color_good
            self.ids.spO2_title.color = color_good

        print(ACR)
        print(DCR)
        print(ACIR)
        print(DCIR)
        print(R)
        print(spo2)
        #print("RoR:" + str(R))
        time.sleep(0.2)


Window.size = (500,700)

Builder.load_file('pulse_ox.kv')

class PulseOxLayout(Widget):
    def record_data(self):
        threading.Thread(target=self.update_label).start()
    
    def update_label(self):
        self.ids.process_data.disabled = True

        back_end(self)

        self.ids.process_data.disabled = False

class PulseOx(App):
    def build(self):
        return PulseOxLayout()

if __name__ == '__main__':
    PulseOx().run()