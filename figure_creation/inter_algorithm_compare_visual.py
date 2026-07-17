import os
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import nibabel as nib
from mpl_toolkits.axes_grid1 import make_axes_locatable

# define the function to plot the figures
def visualize_results(data_matrix, output_path, panel_letter):
    # Set visualization parameters
    vmin_img, vmax_img = 0, 2
    vmin_diff, vmax_diff = -0.2, 0.2

    row_labels = ["Image-based", "Type-2 NUFFT", "Type-1 NUFFT"]
    col_labels = ["Image-based", "Type-2 NUFFT", "Type-1 NUFFT"]

    # plot
    fig = plt.figure(figsize=(11, 12))

    # Force subplots to occupy 100% of the figure frame space
    fig.subplots_adjust(left=0.05, right=1, bottom=0, top=0.95)

    # Adjusted width_ratios for thin row labels
    gs = GridSpec(3, 4, width_ratios=[0.05, 1, 1, 1], wspace=0.15, hspace=0.08)

    # Add the Panel Letter right up against the top-left boundary
    fig.text(0.01, 0.99, panel_letter, fontsize=32, weight='bold', fontname='Arial', ha='left', va='top')

    for r in range(3):
        # A. Add Row Label (Rotated and centered)
        ax_label = fig.add_subplot(gs[r, 0])
        ax_label.text(0.5, 0.5, row_labels[r], ha='center', va='center', rotation=90,
                    fontsize=20, weight='bold', fontname='Arial')
        ax_label.axis('off')

        for c in range(3):
            data = data_matrix[r][c]
            if data is not None:
                ax = fig.add_subplot(gs[r, c + 1])
                
                # Determine scale logic
                is_diag = (r == c)
                curr_vmin = vmin_img if is_diag else vmin_diff
                curr_vmax = vmax_img if is_diag else vmax_diff
                
                # Plot Image
                im = ax.imshow(data, cmap='gray', origin='lower', vmin=curr_vmin, vmax=curr_vmax)
                ax.axis('off')

                # B. Attach Colorbar "Next to Image"
                divider = make_axes_locatable(ax)
                cax = divider.append_axes("right", size="7%", pad=0.05)
                
                if is_diag:
                    ticks = [vmin_img, (vmin_img + vmax_img)/2, vmax_img]
                    fmt = '%.1f'
                else:
                    ticks = [vmin_diff, 0, vmax_diff]
                    fmt = '%.1f'
                
                cbar = plt.colorbar(im, cax=cax, ticks=ticks)
                cbar.ax.tick_params(labelsize=12)
                cbar.ax.set_yticklabels([fmt % t for t in ticks], fontname='Arial', weight='bold')

                # C. Move Column Titles to the BOTTOM
                if r == 2:
                    ax.text(0.5, -0.05, col_labels[c], transform=ax.transAxes,
                            ha='center', va='top', fontsize=20, weight='bold', fontname='Arial')

    # Save with exact zero padding around the bounding box elements
    plt.savefig(output_path, format='svg', dpi=300, bbox_inches='tight', pad_inches=0)
    # plt.show()
    plt.close()

# Define the path to the folder
phantom_data_folder = '../experiments/phantom_results'
real_data_folder = '../experiments/real_scan_results'

# extract z-slices index
phantom_idx=96
real_idx=165

# Filter the list of folders first to ensure the counter/index matches your selection
target_folders = [
    f for f in os.listdir(phantom_data_folder)
    if f in (
        'BrainMRIMotionDB_2021-02-18_15_18_49447_Prospective-TracOline-Patient-5Y',
        'BrainMRIMotionDB_2021-02-26_13_13_45700_Prospective-TracOline-Patient-8Y',
    )
]

#! visualise the phantom and real data results for both trajectories
for folder_name in target_folders:
    if folder_name ==target_folders[0]:
        panel_letter = '(a)'
    elif folder_name == target_folders[1]:
        panel_letter = '(b)'
    # Construct the full paths to the NIfTI files
    type1_original_phantom_path = os.path.join(phantom_data_folder, folder_name, 'type1_original.nii.gz')
    type1_original_real_path = os.path.join(real_data_folder, folder_name, 'type1_original.nii.gz')
    type2_phantom_path = os.path.join(phantom_data_folder, folder_name, 'type2.nii.gz')
    type2_real_path = os.path.join(real_data_folder, folder_name, 'type2.nii.gz')
    image_based_phantom_path = os.path.join(phantom_data_folder, folder_name, 'image_based.nii.gz')
    image_based_real_path = os.path.join(real_data_folder, folder_name, 'image_based.nii.gz')

    # Load the NIfTI images
    type1_original_phantom = nib.load(type1_original_phantom_path).get_fdata()
    type2_phantom = nib.load(type2_phantom_path).get_fdata()
    image_based_phantom = nib.load(image_based_phantom_path).get_fdata()
    type1_original_real = nib.load(type1_original_real_path).get_fdata()
    type2_real = nib.load(type2_real_path).get_fdata()
    image_based_real = nib.load(image_based_real_path).get_fdata()

    # do the subtraction to get the difference images first for real images
    type1_original_minus_type2_real = type1_original_real - type2_real
    type1_original_minus_image_based_real = type1_original_real - image_based_real
    type2_minus_image_based_real = type2_real - image_based_real
    type1_original_minus_type2_phantom = type1_original_phantom - type2_phantom
    type1_original_minus_image_based_phantom = type1_original_phantom - image_based_phantom
    type2_minus_image_based_phantom = type2_phantom - image_based_phantom

    # extract the axial slices for visualization
    image_based_phantom_slice = image_based_phantom[:, :, phantom_idx].T
    type2_phantom_slice = type2_phantom[:, :, phantom_idx].T
    type1_original_phantom_slice = type1_original_phantom[:, :, phantom_idx].T
    image_based_real_slice = image_based_real[:, :, real_idx].T
    type2_real_slice = type2_real[:, :, real_idx].T
    type1_original_real_slice = type1_original_real[:, :, real_idx].T
    type1_original_minus_type2_real_slice = type1_original_minus_type2_real[:, :, real_idx].T
    type1_original_minus_image_based_real_slice = type1_original_minus_image_based_real[:, :, real_idx].T
    type2_minus_image_based_real_slice = type2_minus_image_based_real[:, :, real_idx].T
    type1_original_minus_type2_phantom_slice = type1_original_minus_type2_phantom[:, :, phantom_idx].T
    type1_original_minus_image_based_phantom_slice = type1_original_minus_image_based_phantom[:, :, phantom_idx].T
    type2_minus_image_based_phantom_slice = type2_minus_image_based_phantom[:, :, phantom_idx].T

    # create the data matrix for visualization
    data_matrix_phantom = [
    [image_based_phantom_slice, None, None],
    [type2_minus_image_based_phantom_slice, type2_phantom_slice, None],
    [type1_original_minus_image_based_phantom_slice, type1_original_minus_type2_phantom_slice, type1_original_phantom_slice]]

    data_matrix_real = [
    [image_based_real_slice, None, None],
    [type2_minus_image_based_real_slice, type2_real_slice, None],
    [type1_original_minus_image_based_real_slice, type1_original_minus_type2_real_slice, type1_original_real_slice]]

    # visualize the results for phantom data
    output_path_phantom = f'fig_phantom_compare_{folder_name}.svg'
    visualize_results(data_matrix_phantom, output_path_phantom, panel_letter)

    # visualize the results for real data
    output_path_real = f'fig_real_compare_{folder_name}.svg'
    visualize_results(data_matrix_real, output_path_real, panel_letter)