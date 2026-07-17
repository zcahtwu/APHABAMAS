import numpy as np
import json
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import re

# Set global font properties for all plots
plt.rcParams.update({
    'font.size': 20,             
    'axes.labelsize': 25,        
    'xtick.labelsize': 20,       
    'ytick.labelsize': 20,       
    'legend.fontsize': 25,       
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial'] 
})

def extract_metric_matrix(data_source, metric_prefix):
    comp_keys = ['type2_with_image_based', 'type1_original_with_image_based', 'type1_original_with_type2']
    return np.array([data_source[f"{metric_prefix}_{key}"][:8] for key in comp_keys])

def quantitative_boxplot(output_path, ssim_data, rmsd_data):
    x = np.arange(8)
    width = 0.25 
    trajectories = [f'{i+1}' for i in range(8)]
    colors = ['#CC6677', '#DDCC77', '#807dba']
    comp_titles = ['Type-2 NUFFT vs. Image-based', 
               'Type-1 NUFFT vs. Image-based', 
               'Type-1 NUFFT vs. Type-2 NUFFT']

    def plot_grouped_bars(ax, data_matrix, y_limit=None):
        """Plots 3 grouped bars per trajectory."""
        for i in range(3):
            offset = (i - 1) * width
            ax.bar(x + offset, data_matrix[i], width, label=comp_titles[i], 
                color=colors[i], edgecolor='black', linewidth=0.8)
        
        ax.set_axisbelow(True)
        ax.grid(True, axis='y', linestyle=':', alpha=0.7)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        if y_limit:
            ax.set_ylim(y_limit)
    fig, axs = plt.subplots(2, 1, figsize=(22, 10), sharex=True)
    # Top Plot: SSIM
    plot_grouped_bars(axs[0], ssim_data, y_limit=(0, 1.0))
    axs[0].yaxis.set_major_locator(MultipleLocator(0.25))
    axs[0].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    axs[0].set_ylabel('Pairwise SSIM', fontweight='bold')
    
    # Bottom Plot: RMSD
    plot_grouped_bars(axs[1], rmsd_data, y_limit=(0, 0.08))
    axs[1].yaxis.set_major_locator(MultipleLocator(0.02))
    axs[1].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    axs[1].set_ylabel('Pairwise RMSD', fontweight='bold')
    axs[1].set_xlabel('Trajectory Index', fontweight='bold')
    
    # X-Ticks
    axs[1].set_xticks(x)
    axs[1].set_xticklabels(trajectories)
    
    # Align Y-axis labels
    fig.align_ylabels(axs)
    
    # Legend
    handles, legend_labels = axs[0].get_legend_handles_labels()
    axs[1].legend(handles, legend_labels, loc='upper center', bbox_to_anchor=(0.5, -0.2), 
            ncol=3, framealpha=1, edgecolor='black', columnspacing=1.5)
    axs[0].text(-0.1, 0.92, '(c)', transform=axs[0].transAxes, 
            fontsize=32, fontweight='bold', va='bottom', ha='left', 
            in_layout=True)
    plt.tight_layout()  # Ensure tight layout before adjusting
    
    # Adjust layout to make room at the bottom
    fig.subplots_adjust(top=0.9, bottom=0.15)
    
    # Save & Show
    plt.savefig(output_path, format='svg', bbox_inches='tight', dpi=300)
    plt.close()

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

# Define the path to the folder
phantom_data_folder = '../experiments/phantom_results'
real_data_folder = '../experiments/real_scan_results'

if os.path.exists(os.path.join(real_data_folder, 'metrics.json')) and os.path.exists(os.path.join(phantom_data_folder, 'metrics.json')):
    with open(os.path.join(real_data_folder, 'metrics.json'), 'r') as f:
        real_metrics = json.load(f)
    with open(os.path.join(phantom_data_folder, 'metrics.json'), 'r') as f:
        phantom_metrics = json.load(f)
else:
    print("Warning: JSON files not found. Stop execution.")
    raise FileNotFoundError("Required JSON files not found.")

brain_ssim = extract_metric_matrix(real_metrics, "SSIM")
phantom_ssim = extract_metric_matrix(phantom_metrics, "SSIM")
brain_rmsd = extract_metric_matrix(real_metrics, "RMSD")
phantom_rmsd = extract_metric_matrix(phantom_metrics, "RMSD")

# load traj_list from metrics
traj_list_real = real_metrics['traj_list']
traj_list_phantom = phantom_metrics['traj_list']
target_order = get_target_trajectory_order("../experiments/data_description.txt")

# dynamically find the swap indices to match the target order presented in the paper
swapped_idx_real = [traj_list_real.index(target) for target in target_order]
swapped_idx_phantom = [traj_list_phantom.index(target) for target in target_order]
brain_ssim = brain_ssim[:, swapped_idx_real]
phantom_ssim = phantom_ssim[:, swapped_idx_phantom]
brain_rmsd = brain_rmsd[:, swapped_idx_real]
phantom_rmsd = phantom_rmsd[:, swapped_idx_phantom]

# Create the boxplots for both brain and phantom data
quantitative_boxplot(
    ssim_data=brain_ssim,
    rmsd_data=brain_rmsd,
    output_path="fig_algorithm_compare_brain_metrics.svg"
)
quantitative_boxplot(
    ssim_data=phantom_ssim,
    rmsd_data=phantom_rmsd,
    output_path="fig_algorithm_compare_phantom_metrics.svg"
)