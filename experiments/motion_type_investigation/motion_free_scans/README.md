# Motion-free scan inputs

[Controlled motion](../) · [Input preparation](../../real_motion_traces/#prepare-inputs)

Place the required local scans here before running controlled-motion simulations:

| Filename | Preparation |
| --- | --- |
| `Motion_free_192_256_256_1mm_1mm_1mm.nii.gz` | Created by the measured-motion phantom driver in `experiments/real_motion_traces/phantom_results/` |
| `normalized_real_data.nii.gz` | Created by real-scan preprocessing in `experiments/real_motion_traces/real_scan_results/` |

Follow [input preparation](../../real_motion_traces/#prepare-inputs),
then copy the needed files here. Phantom-only runs need only the phantom;
real-brain-only runs need only the normalised brain image. These files are
ignored by Git.
