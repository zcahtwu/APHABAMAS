import numpy as np
import matplotlib.pyplot as plt
import json
import os
from scipy.spatial.transform import Rotation as R
from matplotlib.ticker import MultipleLocator

# GLOBAL FONT SETTINGS
plt.rcParams.update({
    'font.size': 20,             # General font size
    'axes.labelsize': 20,        # X and Y labels
    'axes.titlesize': 18,        # Title size
    'xtick.labelsize': 20,       # X-axis tick numbers
    'ytick.labelsize': 20,       # Y-axis tick numbers
    'legend.fontsize': 20,       # Legend size
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial'] # Target Arial
})

# Function to convert timestamp to seconds (ignoring hour)
def to_seconds(timestamp):
    # Split the time into components
    hour, minute, second = timestamp.split(":")
    # extract the first hour and set it to be time 0
    # Convert minute and second to total seconds (ignore the hour and microseconds)
    total_seconds = int(hour) * 3600 + int(minute) * 60 + (float(second))
    return total_seconds

# define input and output folder
input_folder = "../experiments/tracking_json/"
output_folder = "trajectories/"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# define TR and total time 
TR = 2.3  # in seconds
total_time = 2.3 * 256
time_points = np.linspace(0, total_time, 256, endpoint=False)
# set colors for x,y,z
colors = ['orange', 'deepskyblue', 'red']
# set y limit for translation and rotation
y_max = 12

# loop over the json files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".json"):
        # load the json file
        with open(os.path.join(input_folder, filename), 'r') as f:
            original_json = json.load(f)

        # Convert each timestamp
        TimeStamp = original_json['MotionData'][0]['TimeStamp']

        # Convert each timestamp to seconds with the first timestamp as 0
        t0 = to_seconds(TimeStamp[0])
        seconds_list = np.array([to_seconds(ts)-t0 for ts in TimeStamp])

        # convert the seconds_list to ignore element larger than total_time
        seconds_list = seconds_list[seconds_list < total_time]

        # extract the matrix elements
        M11 = original_json['MotionData'][0]['M11']
        M12 = original_json['MotionData'][0]['M12']
        M13 = original_json['MotionData'][0]['M13']
        M14 = original_json['MotionData'][0]['M14']
        M21 = original_json['MotionData'][0]['M21']
        M22 = original_json['MotionData'][0]['M22']
        M23 = original_json['MotionData'][0]['M23']
        M24 = original_json['MotionData'][0]['M24']
        M31 = original_json['MotionData'][0]['M31']
        M32 = original_json['MotionData'][0]['M32']
        M33 = original_json['MotionData'][0]['M33']
        M34 = original_json['MotionData'][0]['M34']

        # convert the matrix elements to matrix
        affine_matrix = np.zeros((len(seconds_list), 4, 4))
        for i in range(len(seconds_list)):
            affine_matrix[i] = np.array([[M11[i], M12[i], M13[i], M14[i]],
                                        [M21[i], M22[i], M23[i], M24[i]],
                                        [M31[i], M32[i], M33[i], M34[i]],
                                        [0, 0, 0, 1]])
        # extract the translation and rotation parameters from affine matrix
        translation = np.zeros((len(seconds_list), 3))
        rotation = np.zeros((len(seconds_list), 3))

        for i in range(len(seconds_list)):
            translation[i] = affine_matrix[i][:3, 3] 
            rotation_matrix = affine_matrix[i][:3, :3]
            r = R.from_matrix(rotation_matrix)
            rotation[i] = r.as_euler('xyz', degrees=True)

        # piece-wise constant trajectory
        translation_trajectory = np.zeros((256, 3))
        rotation_trajectory = np.zeros((256, 3))
        shown_time_points = np.zeros(256)
        for i in range(1, 256):
            # find the closest time point
            time_point_index = np.argmin(np.abs(seconds_list - time_points[i]))
            translation_trajectory[i] = translation[time_point_index]
            rotation_trajectory[i] = rotation[time_point_index]
            shown_time_points[i] = seconds_list[time_point_index]

        #! first plot the tracking data
        # Set up the figure with two stacked subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

        # 1. Plot Translation (Top Subplot)
        for i, label in enumerate(['$T_x$', '$T_y$', '$T_z$']):
            ax1.plot(seconds_list, translation[:, i], label=label, color=colors[i], alpha=0.8)

        final_time = seconds_list[-1]
        ax1.axvline(x=final_time, color='black', linestyle='--', linewidth=1.5)

        ax1.set_ylabel('Translation (mm)')
        ax1.set_ylim(-y_max, y_max)
        # Set Y-axis grid every 5 units
        ax1.yaxis.set_major_locator(MultipleLocator(5))
        ax1.legend(loc='upper right', ncol=3, framealpha=0.5)
        ax1.grid(True, axis='y', linestyle=':', alpha=0.7)

        # 2. Plot Rotation using Theta (Bottom Subplot)
        for i, label in enumerate(['$\\theta_x$', '$\\theta_y$', '$\\theta_z$']):
            ax2.plot(seconds_list, rotation[:, i], label=label, color=colors[i], alpha=0.8)

        # Vertical marker for final time on bottom plot
        ax2.axvline(x=final_time, color='black', linestyle='--', linewidth=1.5)

        # Add final time to X-axis ticks
        xticks = list(ax2.get_xticks())
        ax2.set_xticks(xticks + [final_time])

        ax2.set_ylabel('Rotation (deg)')
        ax2.set_xlabel('Time (s)')
        ax2.set_xlim(0, final_time)
        ax2.set_ylim(-y_max, y_max)
        # Set Y-axis grid every 5 units
        ax2.yaxis.set_major_locator(MultipleLocator(5))
        ax2.legend(loc='upper right', ncol=3, framealpha=0.5)
        ax2.grid(True, axis='y', linestyle=':', alpha=0.7)

        plt.tight_layout()
        output_path = os.path.join(output_folder, filename[17:-5] + '_tracking.svg')
        plt.savefig(output_path, dpi=300)

        #! now plot the piece-wise constant trajectory
        # Set up the figure with two stacked subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

        # 1. Plot Translation (Top Subplot)
        for i, label in enumerate(['$T_x$', '$T_y$', '$T_z$']):
            ax1.step(time_points, translation_trajectory[:, i], where='post', label=label, color=colors[i], alpha=0.8)
        ax1.set_ylabel('Translation (mm)')
        ax1.set_ylim(-y_max, y_max)
        # Set Y-axis grid every 5 units
        ax1.yaxis.set_major_locator(MultipleLocator(5))
        ax1.legend(loc='upper right', ncol=3, framealpha=0.5)
        ax1.grid(True, axis='y', linestyle=':', alpha=0.7)

        # 2. Plot Rotation using Theta (Bottom Subplot)
        for i, label in enumerate(['$\\theta_x$', '$\\theta_y$', '$\\theta_z$']):
            ax2.step(time_points, rotation_trajectory[:, i], where='post', label=label, color=colors[i], alpha=0.8)
        
        ax2.set_xticks(xticks + [final_time])
        ax2.set_ylabel('Rotation (deg)')
        ax2.set_xlabel('Time (s)')
        ax2.set_xlim(0, total_time)
        ax2.set_ylim(-y_max, y_max)
        # Set Y-axis grid every 5 units
        ax2.yaxis.set_major_locator(MultipleLocator(5))
        ax2.legend(loc='upper right', ncol=3, framealpha=0.5)
        ax2.grid(True, axis='y', linestyle=':', alpha=0.7)

        plt.tight_layout()
        output_path = os.path.join(output_folder, filename[17:-5] + '_piecewise_constant.svg')
        plt.savefig(output_path, dpi=300)