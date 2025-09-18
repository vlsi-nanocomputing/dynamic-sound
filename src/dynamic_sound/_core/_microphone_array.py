
import numpy as np
from collections import namedtuple
import random
from scipy.spatial.transform import Rotation

class CustomArray:
    MicPCB = namedtuple('MicPCB', ['mics', 'faces'])
    
    @staticmethod
    def rotate_points(points: np.ndarray, angle_z: float, angle_y: float, angle_x: float) -> np.ndarray:
        R= Rotation.from_euler('zyx', [angle_z, angle_y, angle_x], degrees=True).as_matrix()
        return R @ points

    def __init__(self, num_external_mics=6, radius_mics=0.012, radius_pcb=0.022, thickness=0.05, sideboard_angle=30, spacing=0.0, rnd_angle=None, rnd_position=None):
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
        
        self.pcb.append(CustomArray.MicPCB(mics=mics, faces=faces))

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

            self.pcb.append(CustomArray.MicPCB(mics=mics, faces=faces))

    def _generate_mics(self, num_mics, radius):
        mics = [(0.0, 0.0, 0.0)]  # center mic
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
    
    def get_microphones(self) -> np.ndarray:
        return np.concatenate([pcb.mics for pcb in self.pcb], axis=1)
