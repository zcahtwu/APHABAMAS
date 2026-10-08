# Modify the img affine of the real scan to align the reference frame at img center
import nibabel as nib
import numpy as np
from pathlib import Path

# load the nii file
script_dir = Path(__file__).resolve().parent
results_dir = script_dir / 'real_motion_traces' / 'real_scan_results'
results_dir.mkdir(parents=True, exist_ok=True)
niff_file = results_dir / 'sub-000103_acq-standard_T1w.nii.gz'
img = nib.load(niff_file)
# define the header
header = img.header
# load the data
data = img.get_fdata()
# normalize the data to range [0,2], with a 99% percentile clipping
data = np.clip(data, 0, np.percentile(data, 99))
data = data - data.min()
data = data / data.max() * 2
print(data.min(),data.max())

# extract the matrix size and pixdim
matrix_size = header['dim'][1:4]
pixdim = header['pixdim'][1:4]

# create a temporary affine matrix to make the image centre at the origin
rotation_component = np.eye(4)
scaling_component = np.eye(4)
scaling_component[0,0] = pixdim[0]
scaling_component[1,1] = pixdim[1]
scaling_component[2,2] = pixdim[2]
translation_component = np.eye(4)
translation_component[:,3] = rotation_component @ scaling_component @ (np.array([-matrix_size[0]/2,-matrix_size[1]/2,-matrix_size[2]/2,1]))
affine = translation_component @ rotation_component @ scaling_component
print(affine)

# set the affine matrix
img.set_sform(affine)
img.set_qform(affine)
# change the alignment from scanner to reference
img.header['qform_code'] = 1
img.header['sform_code'] = 1

# update the data
img = nib.Nifti1Image(data, img.affine, img.header)

# save the nii file
nib.save(img, results_dir / 'normalized_real_data.nii.gz')
