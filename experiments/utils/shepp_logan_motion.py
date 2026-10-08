# This file define how to simulate motion artifacts based on the analytical phantom.
import numpy as np
from numpy.fft import fftn, ifftn, fftshift
import time
from joblib import Parallel, delayed

# Define a class to simulate motion artifacts
class SheppLoganMotionSimulator:
    '''
    This class is used to simulate motion artifacts on the Shepp Logan phantom. 
    It makes use of the analytical expression for the k-space signal of an ellipsoid.

    The class is initialized with the following parameters:
        matrix_size: tuple/list/array
            The matrix size of the image in x, y, z order.
        trajectory: array
            The trajectory of the motion. It is should have 7 columns. The first columns records the time point where each motion states starts
            column 2-4 are the translation in x, y, and z. The last 3 columns are the rotation in x, y, and z. #! Currently the time point is still seperate from the trajectory
        time_points: array
            The time points at which the motion happens. It is a 1D array, indecating the idx of FE lines where the motions happen.
            #! This should be combined into the trajectory, but for now, it is a separate parameter as it is easier to implement.
        delta_r: tuple
            The voxel sizes in each dimension in x, y, z order. The voxels are isotropic. The default value is (1, 1, 1).
    
    A few parameters of the ellipsoids are predefined in the class. These are:
        axis_lengths: array
            The axis lengths of the ellipsoids. It is a 10x3 array.
        rho: array
            The density values of the ellipsoids. It is a 1D array.
        phi: array
            The rotation angles of the ellipsoids. It is a 10x3 array.
        initial_R_array: array
            The initial rotation matrix of the ellipsoids. It is a 10x3x3 array.
        initial_offset_array: array
            The initial offset of the ellipsoids. It is a 3x10 array.
    '''

    def __init__(self, matrix_size, trajectory=None,time_points=None, delta_r = (1,1,1),object_size_scaling = None):
        # extract the image size if it is a single integer or float
        if isinstance(matrix_size, (int, float)):
            self.matrix_size = (matrix_size, matrix_size, matrix_size)
        elif isinstance(matrix_size, (list, tuple, np.ndarray)):
            self.matrix_size = matrix_size

        # extract dx from delta_r
        self.dx, self.dy, self.dz = delta_r

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
        
        # set up the predefined ellipsoid parameters, they will be scared by voxel size along z-axis
        if object_size_scaling is None:
            self.object_size_scaling = self.matrix_size[-2] * self.dy
        else:
            self.object_size_scaling = object_size_scaling
        
        self.axis_lengths = np.array([[0.69, 0.92, 0.90],
                                [0.6624, 0.874, 0.88],
                                [0.41, 0.16, 0.21],
                                [0.31, 0.11, 0.22],
                                [0.21, 0.25, 0.5],
                                [0.046, 0.046, 0.046],
                                [0.046, 0.023, 0.02],
                                [0.046, 0.023, 0.02],
                                [0.056,0.04, 0.1],
                                [0.056, 0.056, 0.1]]) / 2 * self.object_size_scaling
        
        # the density values
        self.rho = np.array([2.0,
                        -0.8,
                        -0.2,
                        -0.2,
                        0.2,
                        0.2,
                        0.1,
                        0.1,
                        0.2,
                        -0.2])
        # the rotation angles
        self.phi = np.array([[0,0,0],
                                [0,0,0],
                                [0,0,3*np.pi/5],
                                [0,0,2*np.pi/5],
                                [0,0,0],
                                [0,0,0],
                                [0,0,0],
                                [0,0,np.pi/2],
                                [0,0,np.pi/2],
                                [0,0,0]])
        # create the rotation matrix the matrix is designed to match the sitk order Z @ X @ Y
        self.initial_R_array = np.zeros((10,3,3))
        for i in range(10):
            self.initial_R_array[i] = create_rotation_matrix_3d(self.phi[i])

        # create the initial offset array, again, scaled by the largest fov in the image space
        self.initial_offset_array = np.array([[0,0,0],
                                            [0,0,0],
                                            [-0.22,0,-0.25],
                                            [0.22,0,-0.25],
                                            [0,0.35,-0.25],
                                            [0,0.1,-0.25],
                                            [-0.08,-0.65,-0.25],
                                            [0.06,-0.65,-0.25],
                                            [0.06,-0.105,0.625],
                                            [0,0.1,0.625]])/2 * self.object_size_scaling
        
        # ensure each of the element in the initial offset array is a column vector
        self.initial_offset_array = self.initial_offset_array.T
        # store the trajectory and time points
        self.trajectory = trajectory
        self.time_points = time_points
    
    def convert_trajectory_to_arrays(self,idx,reshape = True):
        '''
        This function is used to convert the trajectory to the k-space coordinates.
        This will require the initial rotation and translation which lead the coorsponding 
        ellipsoid to the initial location. The motion affine will be applied after the first
        affine transformation.
        Input:
            idx: int
                The index of the ellipsoid.
            reshape: bool
                If True, the output will be reshaped for both k_space_offsets and k_space_rotation.
        Output:
            k_space_offsets: array
                The k-space offsets for each k-space point. It is a 3D array.
            k_space_rotation: array
                The rotation matrices for each k-space point. It is a 4D array.
            PE_s_idx: array
                The slowest phase encoding plane index.
            PE_o_idx: array
                The other phase encoding index.
        '''
        # extract the initial rotation matrix and translation which need to be combined with the motion
        rotation_matrix_initial = self.initial_R_array[idx]
        translation_initial = self.initial_offset_array[:,idx]

        # calculate the initial affine matrix
        initial_affine_matrix = np.eye(4)
        initial_affine_matrix[0:3,0:3] = rotation_matrix_initial
        initial_affine_matrix[0:3,3] = translation_initial

        # extract the trajectory and time points
        time_points = self.time_points
        translation = self.trajectory[:,0:3]
        # convert the rotation to radians
        rotation = np.radians(self.trajectory[:,3:6])
        # create the rotation matrix
        rotation_matrix = np.zeros((self.trajectory.shape[0],3,3))
        for i in range(self.trajectory.shape[0]):
            rotation_matrix[i] = create_rotation_matrix_3d(rotation[i])

        # create the affine matrix for each time point
        affine_matrix_motion = np.tile(np.eye(4),(len(time_points)-1,1,1))
        #! The below loop may be vectorized later, but since it is only filling in the values, it is not a priority
        for i in range(len(time_points)-1):
            # fill in the rotation
            affine_matrix_motion[i,0:3,0:3] = rotation_matrix[i,:,:]
            # fill in the translation
            affine_matrix_motion[i,0:3,3] = translation[i,:]

        # calculate the combined affine matrix
        combined_affine_matrix = np.matmul(affine_matrix_motion,initial_affine_matrix)

        # extract the effective rotation and translation
        effective_rotation_matrix = combined_affine_matrix[:,0:3,0:3]
        effective_translation = combined_affine_matrix[:,0:3,3]

        # now convert trajectory to the k-space coordinates
        k_space_offsets = np.zeros((self.matrix_size[0],self.matrix_size[1],self.matrix_size[2],3))
        k_space_rotation = np.zeros((self.matrix_size[0],self.matrix_size[1],self.matrix_size[2],3,3))

        # extract the PE_s and PE_o indices, the PE_slow is the slowest phase encoding plane
        # which aligns with the y-axis and the PE_other is the other phase encoding plane 
        # which aligns with the x-axis by default
        #! additional choice can be added to allow the user to choose the PE_slow and PE_other later
        PE_s_idx = np.floor(time_points / self.matrix_size[0]).astype(int)
        PE_o_idx = np.round(time_points % self.matrix_size[0]).astype(int)[1:]

        # Iterate over the trajectory
        for i in range(len(PE_s_idx)-1):
            # first the offsets
            k_space_offsets[:,PE_s_idx[i]:PE_s_idx[i+1],:,:] = effective_translation[i,:]

            # then the rotations
            k_space_rotation[:,PE_s_idx[i]:PE_s_idx[i+1],:,:,:] = effective_rotation_matrix[i,:,:]

        # Then correct the phase encoding plane that the motion happend
        for j in range(len(PE_o_idx)-1):
            # first the offsets
            k_space_offsets[0:PE_o_idx[j],PE_s_idx[j+1],:,:] = effective_translation[j,:]
            # then the rotations
            k_space_rotation[0:PE_o_idx[j],PE_s_idx[j+1],:,:,:] = effective_rotation_matrix[j,:]
        
        # flatten the arrays if needed
        if reshape:
            k_space_offsets = k_space_offsets.reshape(-1,3)
            k_space_rotation = k_space_rotation.reshape(-1,3,3)

        return k_space_offsets, k_space_rotation, PE_s_idx, PE_o_idx
        
    def convert_trajectory_to_arrays(self, idx, reshape=True):
        '''
        This function is used to convert the trajectory to the k-space coordinates.
        This will require the initial rotation and translation which lead the corresponding 
        ellipsoid to the initial location. The motion affine will be applied after the first
        affine transformation.
        '''
        # Extract the initial rotation matrix and translation which need to be combined with the motion
        rotation_matrix_initial = self.initial_R_array[idx]
        translation_initial = self.initial_offset_array[:, idx]

        # Calculate the initial affine matrix
        initial_affine_matrix = np.eye(4)
        initial_affine_matrix[0:3, 0:3] = rotation_matrix_initial
        initial_affine_matrix[0:3, 3] = translation_initial

        # Extract the trajectory and time points
        time_points = self.time_points
        translation = self.trajectory[:, 0:3]
        rotation = np.radians(self.trajectory[:, 3:6])

        # Create the rotation matrix for all time points in a vectorized manner
        rotation_matrices = np.array([create_rotation_matrix_3d(rot) for rot in rotation])

        # Create the affine matrix for each time point in a vectorized manner
        affine_matrices_motion = np.zeros((len(time_points) - 1, 4, 4))
        affine_matrices_motion[:, 0:3, 0:3] = rotation_matrices
        affine_matrices_motion[:, 0:3, 3] = translation

        # Calculate the combined affine matrix
        combined_affine_matrix = np.matmul(affine_matrices_motion, initial_affine_matrix)

        # Extract the effective rotation and translation
        effective_rotation_matrix = combined_affine_matrix[:, 0:3, 0:3]
        effective_translation = combined_affine_matrix[:, 0:3, 3]

        # Initialize the k-space arrays
        k_space_offsets = np.zeros((self.matrix_size[0], self.matrix_size[1], self.matrix_size[2], 3))
        k_space_rotation = np.zeros((self.matrix_size[0], self.matrix_size[1], self.matrix_size[2], 3, 3))

        # Extract the PE_s and PE_o indices
        PE_s_idx = np.floor(time_points / self.matrix_size[0]).astype(int)  # Ensure integer indexing
        PE_o_idx = np.round(time_points % self.matrix_size[0]).astype(int)[1:]  # Ensure integer indexing

        # Perform batch assignment for k-space offsets and rotations
        for i in range(len(PE_s_idx) - 1):
            k_space_offsets[:, PE_s_idx[i]:PE_s_idx[i + 1], :, :] = effective_translation[i, None, :]
            k_space_rotation[:, PE_s_idx[i]:PE_s_idx[i + 1], :, :, :] = effective_rotation_matrix[i, None, :, :]

        # Handle phase encoding corrections (PE_o_idx), batch them if possible
        if np.any(PE_o_idx > 0):  # Only proceed if PE_o_idx contains valid indices (non-zero)
            for j in range(len(PE_o_idx) - 1):
                k_space_offsets[0:PE_o_idx[j], PE_s_idx[j + 1], :, :] = effective_translation[j, None, :]
                k_space_rotation[0:PE_o_idx[j], PE_s_idx[j + 1], :, :, :] = effective_rotation_matrix[j, None, :, :]

        # Reshape if needed
        if reshape:
            k_space_offsets = k_space_offsets.reshape(-1, 3)
            k_space_rotation = k_space_rotation.reshape(-1, 3, 3)

        return k_space_offsets, k_space_rotation, PE_s_idx, PE_o_idx
    
    def create_ellipsoid_k_space_signal_motion_vectorized(self,idx,R_array_motion=None,offset_array_motion=None):
        '''
        This function is used to calculate the k-space signal for a single ellipsoid.
        Input:
            idx: int
                The index of the ellipsoid.
            R_array_motion: array
                The rotation matrices for each k-space point. It is a 4D array. By default, it is None.
            offset_array_motion: array
                The k-space offsets for each k-space point. It is a 3D array. Assume None by default.
        Output:
            k_space_signal: array
                The k-space signal for the idx-th ellipsoid.
        '''

        # extract the variables
        axis_length = self.axis_lengths[idx]
        rho = self.rho[idx]
        initial_offset_array = self.initial_offset_array[:,idx]        
        initial_R_array = self.initial_R_array[idx]
        # unpack the axis lengths
        a, b, c = axis_length

        # Rotate the k-space coordinates using the rotation matrices
        rotated_k_array = np.zeros_like(self.k_coords)

        # uses einsum to calculate the above loop for speed
        if R_array_motion is None:
            rotated_k_array = np.dot(initial_R_array.T, self.k_coords.T).T
        # if motion is involved, then rotate the k-space coordinates using the rotation matrices for motion after the initial rotation
        else:
            # uses einsum to calculate for speed
            #! All the k-space coordinates are stored in a transposed manner, i.e. k_coords = [kx,ky,kz]
            #! hence what we need is (R.T * [kx,ky,kz].T).T = ([kx,ky,kz].T).T * R = k_coords * R_array_motion
            rotated_k_array = np.einsum('ij,ijk->ik', self.k_coords, R_array_motion)
            #! the below line is effectively applying R to [kx,ky,kz].T, left here only for testing purpose.
            # rotated_k_array = np.einsum('ijk,ik->ij', R_array_motion, self.k_coords)

        # Extract individual components of rotated k-vector
        k_hat_x, k_hat_y, k_hat_z = rotated_k_array[..., 0], rotated_k_array[..., 1], rotated_k_array[..., 2]

        # Calculate K values
        K = np.sqrt((a * k_hat_x)**2 + (b * k_hat_y)**2 + (c * k_hat_z)**2)

        # Calculate intermediate_term1 for two cases
        intermediate_term1 = np.zeros_like(K)
        # Condition where K > 0.002
        mask_large_K = K > 0.002
        K_large = K[mask_large_K]
        intermediate_term1[mask_large_K] = (
        (np.sin(2 * np.pi * K_large) - 2 * np.pi * K_large * np.cos(2 * np.pi * K_large)) /
        (2 * np.pi**2 * K_large**3)
        ) #? There will be a numerical difference about 2e-16 when calculating K**3 comparing with the loop version due to numpy power function

        # Condition where K <= 0.002 (Use Taylor series)
        mask_small_K = ~mask_large_K  # Equivalent to (K <= 0.002)
        K_small = K[mask_small_K]
        intermediate_term1[mask_small_K] = (
        4 / 3 * np.pi - 8 / 15 * np.pi**3 * K_small**2 + 8 / 105 * np.pi**5 * K_small**4
        )

        # Calculate intermediate_term2 which is the phase shift due to the offset
        start = time.time()
        if R_array_motion is None:
            intermediate_term2 = np.exp(-1j * 2 * np.pi * np.dot(self.k_coords, initial_offset_array))
        else:
            intermediate_term2 = np.exp(-1j * 2 * np.pi * np.einsum('ij,ij->i', self.k_coords, offset_array_motion))
            # intermediate_term2 = np.exp(-1j * 2 * np.pi * np.sum(self.k_coords * offset_array_motion, axis=-1)) #! This is the original version which is slower
        # Calculate k-space signal
        k_space_signal = (rho * a * b * c * intermediate_term2 * intermediate_term1).reshape(self.matrix_size)

        return k_space_signal
    
    # define the function to calculate the final k-space signal for a single ellipsoid
    def single_ellipsoid_k_space_signal_motion(self,idx, motion = True):
        '''
        This function is used to calculate the k-space signal for a single ellipsoid.
        Input:
            idx: int
                The index of the ellipsoid.
            motion: bool
                If True, the motion will be simulated. If False, the motion will not be simulated,
                and any trajectory will be ignored.
        Output:
            k_space_signal: array
                The k-space signal for the idx-th ellipsoid.
        '''
        if motion:
            # first convert the trajectory to arrays
            offset_array, R_array_motion,_,_ = self.convert_trajectory_to_arrays(idx)
        else:
            offset_array, R_array_motion = None, None
        # calculate the k-space signal for each ellipsoid
        k_space_signal = self.create_ellipsoid_k_space_signal_motion_vectorized(idx,R_array_motion,offset_array)
        
        return k_space_signal
    # define the function to combine multiple ellipsoids
    def combine_ellipsoid_k_space_signal_motion(self, motion = True):
        '''
        This function is used to combine the k-space signal for all the ellipsoids.
        Input:
            motion: bool
                If True, the motion will be simulated. If False, the motion will not be simulated,
                and any trajectory will be ignored.
        Output:
            k_space_signal_combined: array
                The combined k-space signal for all the ellipsoids. It is a 3D array.
        '''
        # loop over each of the ellipsoids and add the signal to the k-space signal (with parallel processing)
        k_space_signals = Parallel(n_jobs=self.rho.shape[0],prefer='threads')(
            delayed(self.single_ellipsoid_k_space_signal_motion)(i, motion) for i in range(self.rho.shape[0])
        )
        k_space_signal_combined = np.zeros(self.matrix_size,dtype=complex)
        for k_space_signal in k_space_signals:
            k_space_signal_combined += k_space_signal
        
        return k_space_signal_combined
    
    # define the function to convert the k-space signal to the image space
    def simulate(self, motion = True, magnitude = True, k_space = False): 
        '''
        This function is used to simulate the phantom based on the analytical solution.
        Input:
            motion: bool
                If True, the motion will be simulated. If False, the motion will not be simulated,
                and any trajectory will be ignored.
            magnitude: bool
                If True, the magnitude value of the reconstructed image will be returned. If False, the 
                complex image will be returned.
            k_space: bool
                If True, the k-space signal will be returned and the magnitude argument will be ignored.
        Output:
            reconstructed_image: array
                The reconstructed image or the signal. It is a 3D array.
        '''
        # first simulate the signal in the k-space, since fft is not unitary and the scaling is applied on the ifft side,
        # the signal is divided by the voxel size to get the correct intensity value
        k_space_signal = self.combine_ellipsoid_k_space_signal_motion(motion)/(self.dx*self.dy*self.dz)
        
        # Perform the inverse fft to get the image space signal, note that fft is not unitary
        reconstructed_image = fftshift(ifftn(fftshift(k_space_signal)))

        # return the magnitude value of the reconstructed image if needed
        if k_space:
            if magnitude != None:
                Warning('Outputting the k-space signal, the magnitude flag is ignored.')
            return k_space_signal
        else:
            if magnitude:
                reconstructed_image = np.abs(reconstructed_image)
            return reconstructed_image
    
    def calculate_rotated_grid_motion(self, inverse = False):
        #! the inverse is only used in case of testing the NUFFT Type 1 simulation methods and should be set as False in all other cases
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

        # extract the PE_s and PE_o indices, the PE_slow is the slowest phase encoding plane
        # which aligns with the y-axis and the PE_other is the other phase encoding plane 
        # which aligns with the x-axis by default
        #! additional choice can be added to allow the user to choose the PE_slow and PE_other later
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
        rotated_k_array = np.einsum('ij,ijk->ik', self.k_coords, k_space_rotation)

        return rotated_k_array
    
    def calculate_phase_ramp_motion(self):
        # extract the trajectory and time points
        time_points = self.time_points
        translation = self.trajectory[:,0:3]

        # now convert trajectory to the k-space coordinates
        k_space_offsets = np.zeros((self.matrix_size[0],self.matrix_size[1],self.matrix_size[2],3))

        # extract the PE_s and PE_o indices, the PE_slow is the slowest phase encoding plane
        # which aligns with the y-axis and the PE_other is the other phase encoding plane 
        # which aligns with the x-axis by default
        #! additional choice can be added to allow the user to choose the PE_slow and PE_other later
        PE_s_idx = np.floor(time_points / self.matrix_size[1]).astype(int)
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

        phase_ramp = np.exp(-1j * 2 * np.pi * np.sum(self.k_coords * k_space_offsets, axis=-1))

        return phase_ramp
    
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

    
# run the below code when this file is run as a script
if __name__ == "__main__":
    # TODO: finish demo
    pass