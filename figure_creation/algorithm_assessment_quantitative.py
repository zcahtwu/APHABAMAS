import matplotlib.pyplot as plt
import numpy as np
import json
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import re

# GLOBAL FONT SETTINGS
plt.rcParams.update({
    'font.size': 20,             
    'axes.labelsize': 20,        
    'xtick.labelsize': 15,       
    'ytick.labelsize': 15,       
    'legend.fontsize': 20,       
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial'] 
})

# Define the input filename
json_filename = '../experiments/phantom_results/metrics.json'
type_1_version = 'original'  # Change to 'adjusted' for the modified version

# --- 1. LOAD AND SLICE DATA ---
with open(json_filename, 'r') as f:
    data = json.load(f)

# Order: Image-Based, Type 2, Type 1
if type_1_version == 'original':
    ssim_keys = ["SSIM_image_based_with_GT", "SSIM_type2_with_GT", "SSIM_type1_original_with_GT"]
    rmse_keys = ["RMSD_image_based_with_GT", "RMSD_type2_with_GT", "RMSD_type1_original_with_GT"]
elif type_1_version == 'adjusted':
    ssim_keys = ["SSIM_image_based_with_GT", "SSIM_type2_with_GT", "SSIM_type1_adjusted_with_GT"]
    rmse_keys = ["RMSD_image_based_with_GT", "RMSD_type2_with_GT", "RMSD_type1_adjusted_with_GT"]
algorithms = ['Image-based', 'Type-2 NUFFT-based', 'Type-1 NUFFT-based']
colors = ['#98df8a', '#ffbb78', '#aec7e8'] 

# Slice data to only take the first 8 trajectories
ssim_results = np.array([data[k][:8] for k in ssim_keys])
rmsd_results = np.array([data[k][:8] for k in rmse_keys])

def get_target_trajectory_order(filepath="DATA_DESCRIPTION.txt"):
    """Reads the text description file and extracts the JSON filenames in order."""
    target_order = []
    with open(filepath, "r") as f:
        for line in f:
            # Look for filenames ending in .json inside quotes
            match = re.search(r'"(BrainMRIMotionDB_.*?)"', line)
            if match:
                target_order.append(match.group(1))
    return target_order

traj_list_phantom = data['traj_list']
target_order = get_target_trajectory_order("../experiments/data_description.txt")
swapped_idx_phantom = [traj_list_phantom.index(target) for target in target_order]
ssim_results = ssim_results[:, swapped_idx_phantom].T
rmsd_results = rmsd_results[:, swapped_idx_phantom].T

trajectories = [f'{i+1}' for i in range(8)]

# --- 2. PLOTTING ---
x = np.arange(len(trajectories)) 
width = 0.25 

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

# Plot 1: SSIM (Top)
for i in range(len(algorithms)):
    offset = (i - 1) * width
    ax1.bar(x + offset, ssim_results[:, i], width, label=algorithms[i], 
            color=colors[i], edgecolor='black', linewidth=0.8)

ax1.set_ylabel('SSIM', fontweight='bold')
ax1.set_ylim(0, 1.0)
ax1.yaxis.set_major_locator(MultipleLocator(0.25)) 
ax1.yaxis.set_major_formatter(FormatStrFormatter('%.2f')) 
ax1.grid(True, axis='y', linestyle=':', alpha=0.7)
# (Legend removed from ax1)

# Plot 2: RMSD (Bottom)
for i in range(len(algorithms)):
    offset = (i - 1) * width
    ax2.bar(x + offset, rmsd_results[:, i], width, label=algorithms[i], 
            color=colors[i], edgecolor='black', linewidth=0.8)

ax2.set_ylabel('RMSD', fontweight='bold')
ax2.set_xlabel('Trajectory Index', fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(trajectories)
ax2.set_ylim(0, 0.08)
ax2.yaxis.set_major_locator(MultipleLocator(0.02)) 
ax2.yaxis.set_major_formatter(FormatStrFormatter('%.2f')) 
ax2.grid(True, axis='y', linestyle=':', alpha=0.7)

# Align Y-labels vertically
fig.align_ylabels([ax1, ax2])

# --- ADD LEGEND TO THE BOTTOM ---
# Grab the handles from ax1 to create the legend
handles, labels = ax1.get_legend_handles_labels()
# Anchor to ax2, pushing it down to y=-0.25 to clear the X-axis label
ax2.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.25), 
           ncol=3, framealpha=1, edgecolor='black', columnspacing=4)

# Final formatting
plt.tight_layout()

# Force extra padding at the bottom of the canvas so the legend isn't cut off
fig.subplots_adjust(bottom=0.25)

# --- 3. SAVE ---
output_path = "fig_algorithm_assessment_quantitative.svg"
plt.savefig(output_path, format='svg', bbox_inches='tight')
# plt.show()
print()