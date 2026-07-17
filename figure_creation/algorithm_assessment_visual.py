import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os

# Set visualization parameters
vmin_img, vmax_img = 0, 2
vmin_img_error, vmax_img_error = -0.2, 0.2
vmin_signal, vmax_signal = 0, 10
vmin_signal_error, vmax_signal_error = -1, 1

# Define the path to the folder
data_folder = '../experiments/phantom_results'
type_1_version = 'original'  # Change to 'adjusted' for the modified version

# Filter the list of files first to ensure the counter/index matches your selection
target_files = [
    f for f in os.listdir(data_folder) 
    if f in (
        'BrainMRIMotionDB_2021-02-18_15_18_49447_Prospective-TracOline-Patient-5Y',
        'BrainMRIMotionDB_2021-02-26_13_13_45700_Prospective-TracOline-Patient-8Y'
    )
]

# Use enumerate to get an index (0, 1, 2...) for naming
for i, filename in enumerate(target_files):
    # load data
    gt_img_path = os.path.join(data_folder, filename, 'GT.nii.gz')
    image_based_img_path = os.path.join(data_folder, filename, 'image_based.nii.gz')
    type2_img_path = os.path.join(data_folder, filename, 'type2.nii.gz')
    if type_1_version =='original':
        type1_img_path = os.path.join(data_folder, filename, 'type1_original.nii.gz')
    elif type_1_version == 'adjusted':
        type1_img_path = os.path.join(data_folder, filename, 'type1_adjusted.nii.gz')
    # load signals
    gt_signal_path = os.path.join(data_folder, filename, 'GT_signal.npy')
    image_based_signal_path = os.path.join(data_folder, filename, 'image_based_signal.npy')
    type2_signal_path = os.path.join(data_folder, filename, 'type2_signal.npy')

    # Load images
    gt_img = nib.load(gt_img_path).get_fdata()
    image_based_img = nib.load(image_based_img_path).get_fdata()
    type2_img = nib.load(type2_img_path).get_fdata()
    type1_img = nib.load(type1_img_path).get_fdata()
    gt_signal = np.load(gt_signal_path)
    image_based_signal = np.load(image_based_signal_path)
    type2_signal = np.load(type2_signal_path)

    # calculate the log-magnitude of the signals for visualization
    gt_signal = np.log(np.abs(gt_signal))
    image_based_signal = np.log(np.abs(image_based_signal))
    type2_signal = np.log(np.abs(type2_signal))

    # Compute difference maps
    error_image_based = image_based_img - gt_img
    error_type2 = type2_img - gt_img
    error_type1 = type1_img - gt_img
    error_signal_image_based = image_based_signal - gt_signal
    error_signal_type2 = type2_signal - gt_signal

    # Extract slices
    gt_slice = gt_img[:,:,96].T
    image_based_slice = image_based_img[:,:,96].T
    type2_slice = type2_img[:,:,96].T
    type1_slice = type1_img[:,:,96].T
    
    error_image_based_slice = error_image_based[:,:,96].T
    error_type2_slice = error_type2[:,:,96].T
    error_type1_slice = error_type1[:,:,96].T

    gt_signal_slice = gt_signal[:,:,128].T
    image_based_signal_slice = image_based_signal[:,:,128].T
    type2_signal_slice = type2_signal[:,:,128].T
    
    error_image_based_signal_slice = error_signal_image_based[:,:,128].T
    error_type2_signal_slice = error_signal_type2[:,:,128].T

    # --- 2. Configure Plot Layout ---
    # Adjusted labels to remove explicit string newlines for clean single-line vertical rotation
    row_configs = [
        ("Simulated Scan", [gt_slice, image_based_slice, type2_slice, type1_slice], vmin_img, vmax_img, 'gray'),
        ("Error Map (Scan)", [None, error_image_based_slice, error_type2_slice, error_type1_slice], vmin_img_error, vmax_img_error, 'gray'),
        ("Simulated Signals", [gt_signal_slice, image_based_signal_slice, type2_signal_slice, None], vmin_signal, vmax_signal, 'gray'),
        ("Error Map (Signals)", [None, error_image_based_signal_slice, error_type2_signal_slice, None], vmin_signal_error, vmax_signal_error, 'gray')
    ]

    col_titles = ["Ground Truth", "Image-based", "Type-2 NUFFT", "Type-1 NUFFT"]

    # --- 3. Figure Generation ---
    fig = plt.figure(figsize=(11.5, 14))
    
    # Adjust layout boundaries to minimize padding around all edges
    fig.subplots_adjust(left=0.05, right=1, bottom=0, top=0.95)
    
    # Narrowed the first column width_ratio to 0.05 for rotated text real estate
    gs = GridSpec(4, 6, width_ratios=[0.1, 1, 1, 1, 1, 0.1], wspace=0.02, hspace=0.1)

    # Add the structural panel letter label at the absolute upper-left corner
    letter = ['a', 'b'][i]
    panel_letter = f"({letter})"
    fig.text(0.01, 0.99, panel_letter, fontsize=32, weight='bold', fontname='Arial', ha='left', va='top')

    for r, config in enumerate(row_configs):
        label_text, data_list, vmin, vmax, cmap = config
        
        # A. Row Label (Rotated 90 degrees on a single line, shifted slightly right via x=0.6)
        ax_label = fig.add_subplot(gs[r, 0])
        ax_label.text(0.5, 0.5, label_text, ha='center', va='center', rotation=90, 
                      fontsize=18, weight='bold', fontname='Arial')
        ax_label.axis('off')

        last_im = None

        # B. Image Columns
        for c, data in enumerate(data_list):
            ax = fig.add_subplot(gs[r, c + 1])
            if data is not None:
                im = ax.imshow(data, cmap=cmap, origin='lower', vmin=vmin, vmax=vmax)
                last_im = im
                if r == 0:
                    ax.set_title(col_titles[c], fontname='Arial', weight='bold', fontsize=18, pad=15)
            ax.axis('off')

        # C. Colorbar Column
        if last_im is not None:
            ax_cbar = fig.add_subplot(gs[r, 5])
            ticks = [vmin, (vmin + vmax) / 2, vmax]
            cbar = plt.colorbar(last_im, cax=ax_cbar, ticks=ticks)
            cbar.ax.tick_params(labelsize=14) 
            cbar.ax.set_yticklabels([f'{t:.1f}' for t in ticks], fontname='Arial', weight='bold')

    # --- 4. Saving ---
    save_name = f"fig_algorithm_assessment_visual_{filename}.svg"
    
    # Enabled strict pad_inches=0 mapping 
    plt.savefig(save_name, format='svg', dpi=300, bbox_inches='tight', pad_inches=0)
    print(f"Saved: {save_name}")
    # plt.show()
    plt.close()
    # break