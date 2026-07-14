import pickle
import os
import numpy as np
from enum import Enum
from tqdm import tqdm
from scipy.spatial.transform import Rotation as R


def data_converter(data_dir, dst_folder=None):
    frames_path = os.path.join(data_dir, 'frames.p')
    frames = pickle.load(open(frames_path, 'rb'))
    if dst_folder is None:
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



def build_airsim_equirect_map(
        src_w=820,
        src_h=400,
        out_w=820,
        out_h=400,
        hfov_deg=128,
        vfov_deg=90,
        pitch_deg=45):

    hfov = np.deg2rad(hfov_deg)
    vfov = np.deg2rad(vfov_deg)
    pitch = np.deg2rad(pitch_deg)

    fx = src_w / (2*np.tan(hfov/2))
    fy = src_h / (2*np.tan(vfov/2))

    cx = src_w/2
    cy = src_h/2


    # output equirettangolare
    az = np.linspace(
        np.deg2rad(-64),
        np.deg2rad(64),
        out_w
    )

    el = np.linspace(
        np.deg2rad(90),
        np.deg2rad(0),
        out_h
    )

    AZ,EL=np.meshgrid(az,el)


    # raggio mondo
    dx=np.cos(EL)*np.cos(AZ)
    dy=np.cos(EL)*np.sin(AZ)
    dz=np.sin(EL)


    # rotazione inversa del pitch
    c=np.cos(-pitch)
    s=np.sin(-pitch)

    X = c*dx - s*dz
    Y = dy
    Z = s*dx + c*dz


    # proiezione pinhole
    map_x = fx*(Y/X)+cx
    map_y = cy - fy*(Z/X)


    # fuori immagine
    invalid=(
        (map_x<0) |
        (map_x>=src_w) |
        (map_y<0) |
        (map_y>=src_h)
    )

    map_x=map_x.astype(np.float32)
    map_y=map_y.astype(np.float32)

    map_x[invalid]=-1
    map_y[invalid]=-1

    return map_x, map_y, invalid

def perspective_to_equirectangular(
        src_img,
        src_w=820,
        src_h=400,
        out_w=820,
        out_h=400,
        hfov_deg=128.0,
        vfov_deg=90.0,
        pitch_deg=45.0,
        interpolation=None,
        border_mode=None):
    import cv2

    if interpolation is None:
        interpolation = cv2.INTER_LINEAR
    if border_mode is None:
        border_mode = cv2.BORDER_CONSTANT

    map_x, map_y, invalid = build_airsim_equirect_map(
        src_w=src_w,
        src_h=src_h,
        out_w=out_w,
        out_h=out_h,
        hfov_deg=hfov_deg,
        vfov_deg=vfov_deg,
        pitch_deg=pitch_deg
    )

    dst_img = cv2.remap(src_img, map_x, map_y, interpolation=interpolation, borderMode=border_mode)
    
    return dst_img, invalid




if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        name_argument = sys.argv[1]
        data_converter(name_argument)
    else:
        print("Please provide the recording path as an argument.")
