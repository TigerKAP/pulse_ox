import neurokit2 as nk
import matplotlib.pyplot as plt

def get_peak_locs(signal):
    cleaned = nk.ppg_clean(signal, sampling_rate=500, heart_rate=None, method='elgendi')    #the sampling rate for the physionet dataset is 500hz
    peaks = nk.ppg_peaks(cleaned, sampling_rate=500, method="elgendi", show=False)    # run peak detection
    return peaks


def plot_with_peaks(r_segment, ir_segment, peak_locs):
    if len(r_segment) == 0 or len(ir_segment) == 0 or len(peak_locs) == 0:
        print("One of the input arrays is empty!")
        return

    print(f"r_segment: {r_segment[:10]}, ir_segment: {ir_segment[:10]}, peak_locs: {peak_locs[:10]}")  # Print some sample data to check

    # Create a figure and two subplots for r_segment and ir_segment
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    # Plot the r_segment with peak markers
    ax1.plot(r_segment, label='R Segment')
    ax1.plot(peak_locs, [r_segment[i] for i in peak_locs], 'ro', label='Peaks')  # Mark peaks with red circles
    ax1.set_title('R Segment with Peaks')
    ax1.set_xlabel('Time (samples)')
    ax1.set_ylabel('Amplitude')
    ax1.legend()

    # Plot the ir_segment with peak markers
    ax2.plot(ir_segment, label='IR Segment')
    ax2.plot(peak_locs, [ir_segment[i] for i in peak_locs], 'ro', label='Peaks')  # Mark peaks with red circles
    ax2.set_title('IR Segment with Peaks')
    ax2.set_xlabel('Time (samples)')
    ax2.set_ylabel('Amplitude')
    ax2.legend()

    # Show the plot
    plt.tight_layout()
    plt.show()