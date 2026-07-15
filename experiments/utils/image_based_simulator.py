'''
Image-Based Motion Simulation modified based on the code from TorchIO library
'''
import nibabel as nib
import numpy as np
import json
import SimpleITK as sitk
from numpy.fft import fftshift, fftn, ifftn
import os

class MotionSimulation:
    def __init__(self, image, trajectory, time_points):
        self.image = sitk.Image(sitk.ReadImage(image))
        self.matrix_size = self.image.GetSize()
        self.trajectory = trajectory
        self.time_points = time_points
    
    def simulate(self,magnitude=True):
        # extract the trajectory and time points
        translation = self.trajectory[:, 0:3]
        rotation = self.trajectory[:, 3:6]
        # convert to lps convention
        rotation[:, 0:2] = -rotation[:, 0:2]
        translation[:, 0:2] = -translation[:, 0:2]
        radians = np.radians(rotation)
        # TODO: allow for different choices of phase encoding direction
        time_points = np.round(self.time_points * self.matrix_size[1],0).astype(int)

        # compute the center of the image in physical space
        center_ijk = np.array(self.image.GetSize()) / 2
        center_physical = self.image.TransformContinuousIndexToPhysicalPoint(center_ijk)

        transformed_img_shape = self.image.GetSize()
        corrupted_signal = np.zeros(transformed_img_shape, dtype=complex)

        motions = []
        # loop over each time point and apply the corresponding transformation
        for i in range(rotation.shape[0]):
            motion = sitk.Euler3DTransform()
            motion.SetCenter(center_physical)
            motion.SetRotation(*radians[i, :])
            motion.SetTranslation(translation[i, :].tolist())
            motion = motion.GetInverse()  # inverse of the motion matrix need to be applied to the grid coordinates
            motions.append(motion)

        transformed_images = []
        for motion_matrix in motions:
            interpolator = sitk.sitkLinear
            resampler = sitk.ResampleImageFilter()
            resampler.SetInterpolator(interpolator)
            resampler.SetReferenceImage(self.image)
            resampler.SetOutputPixelType(sitk.sitkFloat32)
            resampler.SetDefaultPixelValue(0)
            resampler.SetTransform(motion_matrix)
            resampled_data = resampler.Execute(self.image)
            resampled_img = sitk.GetArrayFromImage(resampled_data).transpose()
            transformed_images.append(resampled_img)

        # initialize the corrupted k-space signal
        corrupted_signal = np.zeros(self.image.GetSize(), dtype=complex)

        for i in range(len(time_points) - 1):
            k_space_signal = fftshift(fftn(fftshift(transformed_images[i])))
            # TODO: allow specifying the acquisition trajectory and change phase encoding direction
            corrupted_signal[:, time_points[i]:time_points[i+1], :] = k_space_signal[:, time_points[i]:time_points[i+1], :]
            
        motion_corrupted_image = fftshift(ifftn(fftshift(corrupted_signal)))
        if magnitude:
            motion_corrupted_image = np.abs(motion_corrupted_image)
        return motion_corrupted_image


# if main:
if __name__ == '__main__':
    # TODO: finish demo
    pass
