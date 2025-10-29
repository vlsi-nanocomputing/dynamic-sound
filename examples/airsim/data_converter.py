import pickle
import os
import numpy as np
from enum import Enum
from tqdm import tqdm
from scipy.spatial.transform import Rotation as R


def data_converter(data_dir):
    frames_path = os.path.join(data_dir, 'frames.p')
    frames = pickle.load(open(frames_path, 'rb'))
    dst_folder = os.path.join(data_dir, "converted")
    os.makedirs(dst_folder, exist_ok=True)
    print(f"destination folder: {dst_folder}")

    class Data(Enum):
        TIMESTAMP = 1
        DRONE_POSITION = 2 # will collect the drone's current position [x, y, z] at each frame
        DRONE_ROTATION = 3
        DRONE_VELOCITY = 4 # will collect the drone's current velocity [vx, vy, vz] at each frame
        CAMERA_POSITION = 5
        CAMERA_ROTATION = 6
        BGR = 7 # will collect BGR (not RGB) images from the scene at each frame
        ROTOR_SPEED = 8 

    # drone path
    data = []
    for frame in tqdm(frames, desc="drone_path.csv"):
        px, py, pz = frame[Data.DRONE_POSITION.name]
        qw, qx, qy, qz = frame[Data.DRONE_ROTATION.name]
        # conversion from NED
        px, py, pz = px, -py, -pz
        qw, qx, qy, qz = qw, qx, -qy, -qz
        data.append([
            frame[Data.TIMESTAMP.name],
            px, py, pz,
            qw, qx, qy, qz,
        ])
    np.savetxt(os.path.join(dst_folder, "drone_path.csv"), data, delimiter=",")

    # rotor profile
    data = []
    for frame in tqdm(frames, desc="rotor_rpm.csv"):
        rotors = frame[Data.ROTOR_SPEED.name]
        data.append([frame[Data.TIMESTAMP.name]] + [rotor["speed"]*30/np.pi for rotor in rotors])
    np.savetxt(os.path.join(dst_folder, "rotor_rpm.csv"), data, delimiter=",")

    # camera path
    data = []
    for frame in tqdm(frames, desc="camera_path.csv"):
        px, py, pz = frame[Data.CAMERA_POSITION.name]
        qw, qx, qy, qz = frame[Data.CAMERA_ROTATION.name]
        # conversion from NED
        px, py, pz = px, -py, -pz
        qw, qx, qy, qz = qw, qx, -qy, -qz
        # airsim_quat = R.from_quat([qw, qx, qy, qz], scalar_first=True)
        # r_z90 = R.from_euler('z', -90, degrees=True)
        # qw, qx, qy, qz = (r_z90 * airsim_quat).as_quat(scalar_first=True)
        data.append([
            frame[Data.TIMESTAMP.name],
            px, py, pz,
            qw, qx, qy, qz
        ])
    np.savetxt(os.path.join(dst_folder, "camera_path.csv"), data, delimiter=",")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        name_argument = sys.argv[1]
        data_converter(name_argument)
    else:
        print("Please provide the recording path as an argument.")
