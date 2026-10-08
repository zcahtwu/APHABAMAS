# Simulation methods

[Experiments](../) · [Setup](../../docs/#setup)

APHABAMAS compares algorithms that use a sampled motion-free image with a
reference computed directly from an analytical phantom. These implementations
are shared by the controlled- and measured-motion studies.

| Module | Method |
| --- | --- |
| [shepp_logan_motion.py](shepp_logan_motion.py) | Analytical 3D Shepp–Logan phantom: motion-free images and ground-truth motion-corrupted signals/images |
| [image_based_simulator.py](image_based_simulator.py) | Transform the image at each motion state and combine acquired Fourier samples |
| [k_space_based_simulator.py](k_space_based_simulator.py) | Type-1 and Type-2 NUFFT simulations, including the Type-1 phase-ramp variant |
| [plot_trajectory.py](plot_trajectory.py) | Plot translations and rotations over acquisition time |

Trajectories have six columns: x/y/z translations in mm, followed by x/y/z
rotations in degrees. Study runners handle timing conversion, metrics, and
file output. Start with a [study entry point](../), rather than running
these modules directly. See Section 2 of the [paper](https://arxiv.org/abs/2607.09945)
for the mathematical formulation.
