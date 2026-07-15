'''
This file contains our own implementations of both k-space simulation algorithms. Modified based on the code by Reguig et al.
'''
import numpy as np
from numpy.fft import fftn, ifftn, fftshift
import nibabel as nib
import finufft
    
def create_rotation_matrix_3d(angles) -> np.ndarray:
    '''
    This function is used to create a 3D rotation matrix based on the input angles. (Z @ X @ Y)
    The positive direction of the rotation is counter-clockwise (for coordinates).

    Input:
        angles: array
            The rotation angles in x, y, and z order.
    Output:
        mat: array
            The 3D rotation matrix.
    '''
    mat_x = np.array([[1., 0., 0.],
                    [0., np.cos(angles[0]), -np.sin(angles[0])],
                    [0., np.sin(angles[0]), np.cos(angles[0])]])

    mat_y = np.array([[np.cos(angles[1]), 0., np.sin(angles[1])],
                    [0., 1., 0.],
                    [-np.sin(angles[1]), 0., np.cos(angles[1])]])

    mat_z = np.array([[np.cos(angles[2]), -np.sin(angles[2]), 0.],
                    [np.sin(angles[2]), np.cos(angles[2]), 0.],
                    [0., 0., 1.]])

    mat = mat_z @ mat_x @ mat_y
    return mat
    

class MotionSimulation:
    def __init__(self, image_path, trajectory, time_points, voxel_size=(1,1,1)):
        self.image = nib.load(image_path).get_fdata()
        self.trajectory = trajectory
        self.time_points = time_points

        # extract the image size
        self.matrix_size = self.image.shape

        # extract dx from delta_r
        self.dx, self.dy, self.dz = voxel_size

        # calculate the image space fov in each dimension
        self.fov_x = self.dx * self.matrix_size[0]
        self.fov_y = self.dy * self.matrix_size[1]
        self.fov_z = self.dz * self.matrix_size[2]
        
        # calculate the dkx, dky, dkz
        self.dkx = 1/self.fov_x
        self.dky = 1/self.fov_y
        self.dkz = 1/self.fov_z
        
        # calculate the max and min values in the k-space in each dimension
        self.kx_min = -(self.matrix_size[0]*self.dkx)/2
        self.kx_max = (self.matrix_size[0]*self.dkx)/2 - self.dkx
        self.ky_min = -(self.matrix_size[1]*self.dky)/2
        self.ky_max = (self.matrix_size[1]*self.dky)/2 - self.dky
        self.kz_min = -(self.matrix_size[2]*self.dkz)/2
        self.kz_max = (self.matrix_size[2]*self.dkz)/2 - self.dkz
        
        # create kx, ky, kz lists
        self.kx_list = np.linspace(self.kx_min, self.kx_max, self.matrix_size[0])
        self.ky_list = np.linspace(self.ky_min, self.ky_max, self.matrix_size[1])
        self.kz_list = np.linspace(self.kz_min, self.kz_max, self.matrix_size[2])
        
        # Create the k-space grid
        self.kx, self.ky, self.kz = np.meshgrid(self.kx_list, self.ky_list, self.kz_list, indexing='ij')
        
        # Stack the k-space coordinates to form a 3xN array
        self.k_coords = np.vstack((self.kx.flatten(), self.ky.flatten(), self.kz.flatten())).T
    
    def calculate_rotated_grid_motion(self, inverse = False):
        #! the inverse is only used in case of testing the NUFFT Type-1 algorithm and should otherwise be set to False 
        # extract the trajectory and time points
        time_points = self.time_points
        # convert the rotation to radians
        rotation = np.radians(self.trajectory[:,3:6])
        # create the rotation matrix
        rotation_matrix = np.zeros((self.trajectory.shape[0],3,3))
        for i in range(self.trajectory.shape[0]):
            if inverse:
                rotation_matrix[i] = create_rotation_matrix_3d(rotation[i]).T
            else:
                rotation_matrix[i] = create_rotation_matrix_3d(rotation[i])

        # now convert trajectory to the k-space coordinates
        k_space_rotation = np.zeros((self.matrix_size[0],self.matrix_size[1],self.matrix_size[2],3,3))

        # extract the PE_s and PE_o indices, the PE_s is the slowest phase encoding
        # which aligns with the y-axis and the PE_other is the other phase encoding(also called slice encoding)
        # which aligns with the x-axis by default
        # TODO additional choices to be added to allow the user to choose the PE_slow and PE_other later
        PE_s_idx = np.floor(time_points / self.matrix_size[0]).astype(int)
        PE_o_idx = np.round(time_points % self.matrix_size[0]).astype(int)[1:]

        # Iterate over the trajectory
        for i in range(len(PE_s_idx)-1):
            # then the rotations
            k_space_rotation[:,PE_s_idx[i]:PE_s_idx[i+1],:,0:,:] = rotation_matrix[i,:,:]

        # Then correct the phase encoding plane that the motion happend
        for j in range(len(PE_o_idx)-1):
            # then the rotations
            k_space_rotation[0:PE_o_idx[j],PE_s_idx[j+1],:,:,:] = rotation_matrix[j,:]

        # flatten the arrays if needed
        k_space_rotation = k_space_rotation.reshape(-1,3,3)
        
        # calculate the combined rotation matrix
        #! All the k-space coordinates are stored in a transposed manner, i.e. k_coords = [kx,ky,kz] (Nx3)
        #! and we need our output to be (Nx3) as well, hence:
        #! output = (R.T * [kx,ky,kz].T).T = ([kx,ky,kz].T).T * R = k_coords * R_array_motion
        rotated_k_array = np.einsum('ij,ijk->ik', self.k_coords, k_space_rotation)

        # define the scaling matrix to counts for the voxel size
        diagnal_matrix = np.diag([self.dx, self.dy, self.dz])
        # diagnal_matrix = np.eye(3)
        rotated_k_array = (rotated_k_array @ diagnal_matrix)* np.pi * 2

        return rotated_k_array,k_space_rotation
        
    def calculate_phase_ramp_motion(self, rotation_matrices=None):
        # extract the trajectory and time points
        time_points = self.time_points
        translation = self.trajectory[:,0:3]

        # now convert trajectory to the k-space coordinates
        k_space_offsets = np.zeros((self.matrix_size[0],self.matrix_size[1],self.matrix_size[2],3))

        # extract the PE_s and PE_o indices, the PE_slow is the slowest phase encoding plane
        # which aligns with the y-axis and the PE_other is the other phase encoding plane 
        # which aligns with the x-axis by default
        # TODO additional choices to be added to allow the user to choose the PE_slow and PE_other later
        PE_s_idx = np.floor(time_points / self.matrix_size[0]).astype(int)
        PE_o_idx = np.round(time_points % self.matrix_size[0]).astype(int)[1:]

        # Iterate over the trajectory
        for i in range(len(PE_s_idx)-1):
            # first the offsets
            k_space_offsets[:,PE_s_idx[i]:PE_s_idx[i+1],:,:] = translation[i,:]

        # Then correct the phase encoding plane that the motion happend
        for j in range(len(PE_o_idx)-1):
            # first the offsets
            k_space_offsets[0:PE_o_idx[j],PE_s_idx[j+1],:,:] = translation[j,:]

        # flatten the arrays if needed
        k_space_offsets = k_space_offsets.reshape(-1,3)

        # the phase ramp is calculated differently for the two NUFFT types
        if rotation_matrices is not None:
            #! for this approach, the translations need to be rotated by multiplying the inverse of the rotation matrix
            k_space_offsets = np.einsum('ijk,ik->ij', rotation_matrices, k_space_offsets)
            #! the below line is equivalent to the above line
            # k_space_offsets = np.einsum('ij,ijk->ik', k_space_offsets, rotation_matrices.transpose(0,2,1))

        phase_ramp = np.exp(-1j * 2 * np.pi * np.sum(self.k_coords * k_space_offsets, axis=-1))

        return phase_ramp
    
    def type1_nufft_algorithm(self, phase_ramp_adjust=True, magnitude=True, eps=1E-7):
        # obtain the fft of the original image
        k_space_signal = fftshift(fftn(fftshift(self.image))).flatten()
        # calculate the rotated grid motion
        rotated_k_array, rotation_matrices = self.calculate_rotated_grid_motion(inverse=True)
        rotated_k_array = rotated_k_array.T
        # calculate the phase ramp motion
        if phase_ramp_adjust:
            phase_ramp = self.calculate_phase_ramp_motion(rotation_matrices)
        else:
            phase_ramp = self.calculate_phase_ramp_motion()
        # calculate the k-space data
        k_space_signal = k_space_signal * phase_ramp

        f = np.zeros(self.image.shape, dtype=np.complex128)
        finufft.nufft3d1(rotated_k_array[0], rotated_k_array[1], rotated_k_array[2], k_space_signal,
                         eps=eps, out=f, debug=0, spread_debug=0, spread_sort=2, fftw=0, modeord=0,
                         chkbnds=0, upsampfac=1.25, isign= 1)
        # normalize the image
        f = f/f.size
        if magnitude:
            f = np.abs(f)
        return f

    def type2_nufft_algorithm(self, magnitude=True, eps=1E-7):
        # calculate the rotated grid motion
        rotated_k_array = self.calculate_rotated_grid_motion()[0].T

        # calculate the phase ramp motion
        phase_ramp = self.calculate_phase_ramp_motion()
        # calculate the k-space data
        f = np.zeros(rotated_k_array[0].shape, dtype=np.complex128).flatten()
        ip = self.image.astype(complex)
        finufft.nufft3d2(rotated_k_array[0], rotated_k_array[1], rotated_k_array[2], ip,
                         eps=eps, out=f, debug=0, spread_debug=0, spread_sort=2, fftw=0, modeord=0,
                         chkbnds=0, upsampfac=1.25, isign=-1)

        f = f * phase_ramp
        f = f.reshape(ip.shape)

        # reconstruct the image
        image = fftshift(ifftn(fftshift(f)))
        if magnitude:
            image = np.abs(image)
        return image
    
    def simulate(self, nufft_type='type2', magnitude=True, phase_ramp_adjust=True, eps=1E-7):
        if nufft_type == 'type1':
            return self.type1_nufft_algorithm(phase_ramp_adjust=phase_ramp_adjust, magnitude=magnitude, eps=eps)
        elif nufft_type == 'type2':
            if phase_ramp_adjust is False:
                print("Warning: phase_ramp_adjust is not applicable for Type-2. Ignoring this parameter.")
            return self.type2_nufft_algorithm(magnitude=magnitude, eps=eps)

if __name__ == '__main__':
    # TODO: finish demo
    pass
