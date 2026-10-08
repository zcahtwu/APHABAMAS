# Paper and setup

[Repository home](https://github.com/zcahtwu/APHABAMAS_temp)

- [Paper on arXiv](https://arxiv.org/abs/2607.09945): theory, experiments, results, and supporting information.
- [Assessment scheme](assessment_scheme.png): the analytical-reference workflow shown on the landing page.

## Setup

Use a dedicated Python environment. For trajectories, statistical analysis,
and metric figures:

```bash
python -m pip install numpy scipy matplotlib pandas
```

For all simulation and figure workflows:

```bash
python -m pip install numpy scipy nibabel SimpleITK finufft matplotlib pandas scikit-image joblib tqdm
```

Dependency versions are unpinned; compatibility across versions has not been
tested.

Run all documented commands from the repository root. Optional image viewers
also need Bash and FSL (`fslmaths` and `fsleyes`).

## Data and outputs

Motion-tracking JSONs, saved metrics, analysis CSVs, and selected SVGs are
included. MRI (`*.nii.gz`) and NumPy (`*.npy`) files must be supplied or
generated locally; each [Guide](../experiments/) explains its inputs.

Synthetic trajectories go to each motion model's `trajectories/` folder;
simulation outputs go to its `results/` folder. Figure SVGs are written beside
their generators. Rerunning commands overwrites outputs with matching names.
