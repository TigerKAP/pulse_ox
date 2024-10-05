import numpy as np
import pandas as pd
import neurokit2 as nk
#%%
# create arrays
ecg_array = np.empty((0, 5000))
labels_array = np.empty((0,5000))
for i in range(1,11):
    # use pandas to import
    ecg_data = pd.read_csv("C:/Users/kaiab/OneDrive/Desktop/Programs/MATLAB Programs/pulse ox/physionet dataset/s1-15_sit_ML/s" + str(i) + "_sit_ML_ecg.csv")  
    labels = pd.read_csv("C:/Users/kaiab/OneDrive/Desktop/Programs/MATLAB Programs/pulse ox/physionet dataset/s1-15_sit_ML/s" + str(i) + "_sit_ML_labels.csv")
    # convert to numpy arrays
    ecg_arr = ecg_data.to_numpy() #each of these will be 40-50 rows of 5000 points/columns
    ecg_array = np.append(ecg_array,ecg_arr,axis=0) # we add curr subject's 40-50 rows below the prev subject's and save to preallocated array
    lab_arr = labels.to_numpy() # repeat for labels.
    labels_array = np.append(labels_array, lab_arr,axis=0)
   
ecg_array_test = np.empty((0, 5000))
labels_array_test = np.empty((0,5000))
for i in range(11,16):
    # use pandas to import
    ecg_data = pd.read_csv("C:/Users/kaiab/OneDrive/Desktop/Programs/MATLAB Programs/pulse ox/physionet dataset/s1-15_sit_ML/s" + str(i) + "_sit_ML_ecg.csv")  # Replace with your actual file name
    labels = pd.read_csv("C:/Users/kaiab/OneDrive/Desktop/Programs/MATLAB Programs/pulse ox/physionet dataset/s1-15_sit_ML/s" + str(i) + "_sit_ML_labels.csv")  # Replace with your actual file name
    # convert to numpy arrays
    ecg_arr = ecg_data.to_numpy()
    ecg_array_test = np.append(ecg_array_test,ecg_arr,axis=0)
    lab_arr = labels.to_numpy()
    labels_array_test = np.append(labels_array_test, lab_arr,axis=0)
   
#%%
   
ppg_array = np.empty((0, 5000))
for i in range(1,11):
    # use pandas to import
    ppg_data = pd.read_csv("C:/Users/kaiab/OneDrive/Desktop/Programs/MATLAB Programs/pulse ox/physionet dataset/s1-15_sit_ML/s" + str(i) + "_sit_ML_ppg.csv")  
    # convert to numpy arrays
    ppg_arr = ppg_data.to_numpy() #each of these will be 40-50 rows of 5000 points/columns
    ppg_array = np.append(ppg_array,ppg_arr,axis=0) # we add curr subject's 40-50 rows below the prev subject's and save to preallocated array
   
#%%

#take the first row of the ecg array
#frow = ecg_array[0][:]

for i in range(len(ppg_array)):
    if (i%39 == 0):
        frow_ppg = ppg_array[i][:]
        cleaned = nk.ppg_clean(frow_ppg, sampling_rate=500, heart_rate=None, method='elgendi')    #the sampling rate for the physionet dataset is 500hz
        peaks = nk.ppg_peaks(cleaned, sampling_rate=500, method="elgendi", show=True)    # run peak detection
#%%

ppg = nk.ppg_simulate(heart_rate=75, duration=20, sampling_rate=50)

ppg[400:600] = ppg[400:600] + np.random.normal(0, 1.25, 200)

# Default method (Elgendi et al., 2013)
peaks, info = nk.ppg_peaks(ppg, sampling_rate=100, method="elgendi", show=True)

info["PPG_Peaks"]

# Method by Bishop et al., (2018)
peaks, info = nk.ppg_peaks(ppg, sampling_rate=100, method="bishop", show=True)

# Correct artifacts
peaks, info = nk.ppg_peaks(ppg, sampling_rate=100, correct_artifacts=True, show=True)