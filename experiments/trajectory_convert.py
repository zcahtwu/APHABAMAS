# this file is used to convert the brainMRI data to piece-wise constant trajectory
import numpy as np
import json
from scipy.spatial.transform import Rotation as R
import os
from tqdm import tqdm

# Function to convert timestamp to seconds (ignoring hour)
def to_seconds(timestamp):
    # Split the time into components
    hour, minute, second = timestamp.split(":")
    # extract the first hour and set it to be time 0
    # Convert minute and second to total seconds (ignore the hour and microseconds)
    total_seconds = int(hour) * 3600 + int(minute) * 60 + (float(second))
    return total_seconds

# define input and output folder
input_folder = "tracking_json/"
output_folder = "piecewise_trajectories/"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# define TR and total time 
TR = 2.3  # in seconds
total_time = 2.3 * 256
# save json flag
save_json = True

# loop over the json files in the input folder
for filename in tqdm(os.listdir(input_folder)):
    if filename.endswith(".json"):
        # load the json file
        with open(os.path.join(input_folder, filename), 'r') as f:
            original_json = json.load(f)

        # Convert each timestamp
        TimeStamp = original_json['MotionData'][0]['TimeStamp']

        # Convert each timestamp to seconds with the first timestamp as 0
        t0 = to_seconds(TimeStamp[0])
        seconds_list = np.array([to_seconds(ts)-t0 for ts in TimeStamp])

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
        affine_matrix = np.zeros((256, 4, 4))
        # create the translation and rotation trajectory
        translation_trajectory = np.zeros((256, 3))
        rotation_trajectory = np.zeros((256, 3))
        time_points = np.linspace(0, total_time, 256, endpoint=False)
        
        for i in range(1, 256):
            # find the closest time point
            time_point_index = np.argmin(np.abs(seconds_list - time_points[i]))
            affine_matrix[i] = np.array([[M11[time_point_index], M12[time_point_index], M13[time_point_index], M14[time_point_index]],
                                        [M21[time_point_index], M22[time_point_index], M23[time_point_index], M24[time_point_index]],
                                        [M31[time_point_index], M32[time_point_index], M33[time_point_index], M34[time_point_index]],
                                        [0, 0, 0, 1]])
            # extract translation and rotation
            translation_trajectory[i] = affine_matrix[i][:3, 3]
            rotation_matrix = affine_matrix[i][:3, :3]
            r = R.from_matrix(rotation_matrix)
            rotation_trajectory[i] = r.as_euler('xyz', degrees=True)

        # add a 0,0,0 at the beginning for both translation and rotation
        normalised_time_points = time_points / total_time
        normalised_time_points = np.hstack((normalised_time_points,1))

        # if save_json is true,
        if save_json:
            # save the translation and rotation trajectory as json
            trajectory = {'time_points': normalised_time_points.tolist(),
                'translation': translation_trajectory.tolist(),
                'rotation': rotation_trajectory.tolist()}
            
            with open(os.path.join(output_folder, filename), 'w') as f:
                json.dump(trajectory, f, indent=4)