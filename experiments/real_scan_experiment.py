import numpy as np
import json
import nibabel as nib
import os
from tqdm import tqdm
from utils.image_based_simulator import MotionSimulation as ImageBasedSimulator
from utils.k_space_based_simulator import MotionSimulation as KSpaceBasedSimulator
from skimage.metrics import structural_similarity as ssim

# define the path to load the motion free digital phantom
motion_free_image_path = 'real_scan_results/normalized_real_data.nii.gz'
motion_free_image = nib.load(motion_free_image_path).get_fdata()

# define the affine matrix of the motion free digital phantom
affine_matrix = nib.load(motion_free_image_path).affine
# extract the matrix size and voxel size
matrix_size = motion_free_image.shape
voxel_size = (1,1,1)

# specify the folder of the trajectory files
trajectory_folder = "piecewise_trajectories/"

# specify the output folder
output_folder = "real_scan_results"

# compare with other algorithms
SSIM_type1_original_with_type2, SSIM_type1_original_with_image_based = [], []
SSIM_type1_adjusted_with_type2, SSIM_type1_adjusted_with_image_based = [], []
SSIM_type2_with_image_based = []
SSIM_type1_original_with_adjusted = []
RMSD_type1_original_with_type2, RMSD_type1_original_with_image_based = [], []
RMSD_type1_adjusted_with_type2, RMSD_type1_adjusted_with_image_based = [], []
RMSD_type2_with_image_based = []
RMSD_type1_original_with_adjusted = []
traj_list = []

for filename in tqdm(os.listdir(trajectory_folder)):
    # if not a json file, skip
    if not filename.endswith('.json'):
        continue
    else:
        traj_name = os.path.splitext(filename)[0]
        traj_list.append(traj_name)
    # create output sub-folder
    if not os.path.exists(f'{output_folder}/{traj_name}'):
        os.makedirs(f'{output_folder}/{traj_name}')
    # load the piece-wise trajectory
    with open(os.path.join(trajectory_folder, filename), 'r') as f:
        piece_wise_trajectory = json.load(f)
        # load translation, rotation, and time_points and convert them to trajectories
        translation = np.array(piece_wise_trajectory['translation'])
        rotation = np.array(piece_wise_trajectory['rotation'])
        time_points = np.array(piece_wise_trajectory['time_points'])
        # the k-space simulator requires the time points to be the idx of readout lines
        time_points_k_space = time_points * matrix_size[0] * matrix_size[1]
        # create the trajectory by vertical stacking the translation and rotation
        trajectory = np.hstack((translation,rotation))
    #! ==================  the k-space based simulation ==================
    k_space_based_simulator = KSpaceBasedSimulator(image_path=motion_free_image_path, trajectory=trajectory, time_points=time_points_k_space)
    # first type 1 without modification:
    type1_result_orignal = k_space_based_simulator.simulate(nufft_type='type1')
    nib.save(nib.Nifti1Image(type1_result_orignal, affine_matrix), f'{output_folder}/{traj_name}/type1_original.nii.gz')
    # type 1 with phase ramp adjustment:
    type1_result_adjusted = k_space_based_simulator.simulate(nufft_type='type1', phase_ramp_adjust=False)
    nib.save(nib.Nifti1Image(type1_result_adjusted, affine_matrix), f'{output_folder}/{traj_name}/type1_adjusted.nii.gz')

    # second type 2:
    type2_result = k_space_based_simulator.simulate(nufft_type='type2')
    nib.save(nib.Nifti1Image(type2_result, affine_matrix), f'{output_folder}/{traj_name}/type2.nii.gz')
    #! ==================  the image based simulation ==================
    image_based_simulator = ImageBasedSimulator(image=motion_free_image_path, trajectory=trajectory, time_points=time_points)
    image_based_result = image_based_simulator.simulate()
    nib.save(nib.Nifti1Image(image_based_result, affine_matrix), f'{output_folder}/{traj_name}/image_based.nii.gz')

    # calculate SSIM and RMSE with other methods
    SSIM_type1_original_with_type2.append(ssim(type1_result_orignal, type2_result, data_range=2))
    SSIM_type1_original_with_image_based.append(ssim(type1_result_orignal, image_based_result, data_range=2))
    SSIM_type1_adjusted_with_type2.append(ssim(type1_result_adjusted, type2_result, data_range=2))
    SSIM_type1_adjusted_with_image_based.append(ssim(type1_result_adjusted, image_based_result, data_range=2))
    SSIM_type2_with_image_based.append(ssim(type2_result, image_based_result, data_range=2))
    RMSD_type1_original_with_type2.append(np.sqrt(np.mean((type1_result_orignal - type2_result) ** 2)))
    RMSD_type1_original_with_image_based.append(np.sqrt(np.mean((type1_result_orignal - image_based_result) ** 2)))
    RMSD_type1_adjusted_with_type2.append(np.sqrt(np.mean((type1_result_adjusted - type2_result) ** 2)))
    RMSD_type1_adjusted_with_image_based.append(np.sqrt(np.mean((type1_result_adjusted - image_based_result) ** 2)))
    RMSD_type2_with_image_based.append(np.sqrt(np.mean((type2_result - image_based_result) ** 2)))

# save the results to a json file
results = {
    'traj_list': traj_list,
    'SSIM_type1_original_with_type2': SSIM_type1_original_with_type2,
    'SSIM_type1_original_with_image_based': SSIM_type1_original_with_image_based,
    'SSIM_type1_adjusted_with_type2': SSIM_type1_adjusted_with_type2,
    'SSIM_type1_adjusted_with_image_based': SSIM_type1_adjusted_with_image_based,
    'SSIM_type2_with_image_based': SSIM_type2_with_image_based,
    'RMSD_type1_original_with_type2': RMSD_type1_original_with_type2,
    'RMSD_type1_original_with_image_based': RMSD_type1_original_with_image_based,
    'RMSD_type1_adjusted_with_type2': RMSD_type1_adjusted_with_type2,
    'RMSD_type1_adjusted_with_image_based': RMSD_type1_adjusted_with_image_based,
    'RMSD_type2_with_image_based': RMSD_type2_with_image_based
}

with open(f'{output_folder}/metrics.json', 'w') as f:
    json.dump(results, f, indent=4)


