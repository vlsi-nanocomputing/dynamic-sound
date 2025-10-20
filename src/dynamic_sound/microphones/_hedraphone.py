from dynamic_sound.microphones import MicrophoneArray

import numpy as np

import random
from collections import namedtuple
from scipy.spatial.transform import Rotation

class Hedraphone(MicrophoneArray):
    MicPCB = namedtuple('MicPCB', ['mics', 'faces'])
    
    @staticmethod
    def rotate_points(points: np.ndarray, angle_z: float, angle_y: float, angle_x: float) -> np.ndarray:
        R= Rotation.from_euler('zyx', [angle_z, angle_y, angle_x], degrees=True).as_matrix()
        return R @ points

    def __init__(self, file_path, num_external_mics=6, radius_mics=0.012, radius_pcb=0.022, thickness=0.05, sideboard_angle=30, spacing=0.0, rnd_angle=None, rnd_position=None, sample_rate = 48_000, sample_width=4):
        self.pcb = []
        mics = self._generate_mics(num_external_mics, radius_mics)
        faces = self._generate_faces(num_external_mics, radius_pcb, thickness)
        
        # randomize pcb angles
        if rnd_angle is not None:
            angle_x = random.uniform(-rnd_angle, rnd_angle)
            angle_y = random.uniform(-rnd_angle, rnd_angle)
            angle_z = random.uniform(-rnd_angle, rnd_angle)
            print(f"rot: {angle_x} {angle_y} {angle_z}")
            mics = self.rotate_points(mics, angle_z, angle_y, angle_x)
            faces = self.rotate_points(faces, angle_z, angle_y, angle_x)

        # randomize pcb positions
        if rnd_position is not None:
            pos_x = random.uniform(-rnd_position, rnd_position)
            pos_y = random.uniform(-rnd_position, rnd_position)
            pos_z = random.uniform(-rnd_position, rnd_position)
            mics = np.array([[pos_x], [pos_y], [pos_z]]) + mics
            faces = np.array([[pos_x], [pos_y], [pos_z]]) + faces
        
        self.pcb.append(self.MicPCB(mics=mics, faces=faces))

        for i in range(num_external_mics):

            mics = self._generate_mics(num_external_mics, radius_mics)
            faces = self._generate_faces(num_external_mics, radius_pcb, thickness)
            
            # randomize pcb angles
            if rnd_angle is not None:
                angle_x = random.uniform(-rnd_angle, rnd_angle)
                angle_y = random.uniform(-rnd_angle, rnd_angle)
                angle_z = random.uniform(-rnd_angle, rnd_angle)
                mics = self.rotate_points(mics, angle_z, angle_y, angle_x)
                faces = self.rotate_points(faces, angle_z, angle_y, angle_x)

            # randomize pcb positions
            if rnd_position is not None:
                pos_x = random.uniform(-rnd_position, rnd_position)
                pos_y = random.uniform(-rnd_position, rnd_position)
                pos_z = random.uniform(-rnd_position, rnd_position)
                mics = np.array([[pos_x], [pos_y], [pos_z]]) + mics
                faces = np.array([[pos_x], [pos_y], [pos_z]]) + faces

            mics = self.rotate_points(mics, angle_z=180.0, angle_y=0.0, angle_x=0.0)
            mics = np.array([[spacing], [0.0], [0.0]]) + mics
            mics = self.rotate_points(mics, angle_z=0.0, angle_y=sideboard_angle, angle_x=0.0)
            mics = np.array([[spacing], [0.0], [0.0]]) + mics
            mics = self.rotate_points(mics, angle_z=i*360.0/num_external_mics, angle_y=0.0, angle_x=0.0)
                
            faces = self.rotate_points(faces, angle_z=180.0, angle_y=0.0, angle_x=0.0)
            faces = np.array([[spacing], [0.0], [0.0]]) + faces
            faces = self.rotate_points(faces, angle_z=0.0, angle_y=sideboard_angle, angle_x=0.0)
            faces = np.array([[spacing], [0.0], [0.0]]) + faces
            faces = self.rotate_points(faces, angle_z=i*360.0/num_external_mics, angle_y=0.0, angle_x=0.0)

            self.pcb.append(self.MicPCB(mics=mics, faces=faces))
        
        positions = np.concatenate([pcb.mics for pcb in self.pcb], axis=1).T
        rotations = np.tile([1, 0, 0, 0], (len(positions), 1))
        super().__init__(np.hstack((positions, rotations)), file_path, sample_rate, sample_width)

    def _generate_mics(self, num_mics, radius):
        mics = [(0.0, 0.0, 0.0)]
        for i in range(num_mics):
            angle = ((2 * np.pi * i) - np.pi) / num_mics
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            z = 0.0
            mics.append((x, y, z))
        return np.array(mics).T

    def _generate_faces(self, num_mics, radius, thickness):
        faces = []
        for i in range(num_mics):
            angle = ((2 * np.pi * i) - np.pi) / num_mics
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            z = 0.0
            faces.append((x, y, z))
        return np.array(faces).T

    def plot_figure(self, show=True, ax=None):
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection

        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
        
        mics = self.get_microphones().T

        ax.scatter(mics[0], mics[1], mics[2], marker='o')
        for pcb in self.pcb:
            ax.add_collection3d(Poly3DCollection([pcb.faces.T], alpha=0.5, facecolor='cyan', edgecolor='k'))
        ax.set_aspect('equal')

        ax.set_title("HedraPhone")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.grid(True)

        if show:
            plt.show()
        return ax


class Hedraphone_v1(Hedraphone):
    def __init__(self, file_path, rnd_angle=None, rnd_position=None, sample_rate=48000, sample_width=4):
        super().__init__(file_path, num_external_mics=5, radius_mics=0.012, radius_pcb=0.022, thickness=0.00155, sideboard_angle=63.43, spacing=0.022, rnd_angle=rnd_angle, rnd_position=rnd_position, sample_rate=sample_rate, sample_width=sample_width)


class Hedraphone_v2(Hedraphone):
    def __init__(self, file_path, rnd_angle=None, rnd_position=None, sample_rate=48000, sample_width=4):
        super().__init__(file_path, num_external_mics=5, radius_mics=0.014, radius_pcb=0.022, thickness=0.00155, sideboard_angle=63.43, spacing=0.022, rnd_angle=rnd_angle, rnd_position=rnd_position, sample_rate=sample_rate, sample_width=sample_width)


