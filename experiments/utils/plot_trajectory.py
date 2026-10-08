import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator


def plot_motion_trajectory(trajectory, time_points, output_path, title=None):
    """Plot translation and rotation using the trajectory-figure style."""
    trajectory = np.asarray(trajectory)
    time_points = np.asarray(time_points)

    # A trajectory describes the pose after each time point. Repeat the final
    # pose when the supplied time_points also contain the acquisition end time.
    if len(time_points) == len(trajectory) + 1:
        trajectory = np.vstack((trajectory, trajectory[-1]))
    elif len(time_points) != len(trajectory):
        raise ValueError(
            'time_points must have the same length as trajectory, or one extra end point'
        )

    colors = ['orange', 'deepskyblue', 'red']
    plot_settings = {
        'font.size': 20,
        'axes.labelsize': 20,
        'axes.titlesize': 18,
        'xtick.labelsize': 20,
        'ytick.labelsize': 20,
        'legend.fontsize': 20,
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Liberation Sans', 'DejaVu Sans']
    }

    with plt.rc_context(plot_settings):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)

        for index, label in enumerate(['$T_x$', '$T_y$', '$T_z$']):
            ax1.step(
                time_points,
                trajectory[:, index],
                where='post',
                label=label,
                color=colors[index],
                alpha=0.8
            )
        ax1.set_ylabel('Translation (mm)')

        for index, label in enumerate(
            ['$\\theta_x$', '$\\theta_y$', '$\\theta_z$']
        ):
            ax2.step(
                time_points,
                trajectory[:, index + 3],
                where='post',
                label=label,
                color=colors[index],
                alpha=0.8
            )
        ax2.set_ylabel('Rotation (deg)')
        ax2.set_xlabel('Normalized acquisition time')
        ax2.set_xlim(0, 1)

        for axis in (ax1, ax2):
            axis.set_ylim(-12, 12)
            axis.yaxis.set_major_locator(MultipleLocator(5))
            axis.legend(loc='upper right', ncol=3, framealpha=0.5)
            axis.grid(True, axis='y', linestyle=':', alpha=0.7)

        if title is not None:
            fig.suptitle(title, y=0.98)

        fig.tight_layout(rect=[0, 0, 1, 0.92])
        fig.savefig(output_path, dpi=300)
        plt.close(fig)
