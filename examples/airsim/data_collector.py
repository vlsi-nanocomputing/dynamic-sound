import airsim
import numpy as np
import subprocess
import json
import time
import pickle
import copy
import psutil
import shutil
import os
import math
from enum import Enum
from pprint import pprint

## ******** ENUMERATED OBJECTS TO SELECT FROM BELOW ******** 
class Maps(Enum):
    BLOCKS = './maps/Blocks/LinuxBlocks1.8.1/LinuxNoEditor/Blocks.sh' # simple shapes and textures
    AIRSIMNH = './maps/AirSimNH/LinuxNoEditor/AirSimNH.sh' # realistic objects such as trees, houses, cars
class Defaults(Enum):
    DEFAULT = './settings/default.json' # basic multirotor quad copter settings
class Modes(Enum):
    POSITION = 1 # will fly drone to desired position at given speed (x, y, z, s)
    DURATION = 2 # will fly drone at constant velocity for given duration (vx, vy, vz, dt)
    TELEPORTATION = 3 # will instantly teleport drone to desired location (x, y, z)
class Data(Enum):
    TIMESTAMP = 1
    DRONE_POSITION = 2 # will collect the drone's current position [x, y, z] at each frame
    DRONE_ROTATION = 3
    DRONE_VELOCITY = 4 # will collect the drone's current velocity [vx, vy, vz] at each frame
    CAMERA_POSITION = 5
    CAMERA_ROTATION = 6
    BGR = 7 # will collect BGR (not RGB) images from the scene at each frame
    ROTOR_SPEED = 8
class Camera(Enum):
    DRONE = 1
    GLOBAL = 2




## ******** USER PARAMETERS ******** 
initial_locals = locals().copy() # exclude above local variables from parameter list
data_dir = 'data/run1/' # writes data to this folder path (WARNING: will overwrite be careful)
airsim_map = Maps.BLOCKS # airsim map to launch and run in 
release_path = airsim_map.value
default_settings = Defaults.DEFAULT
base_settings_path = default_settings.value # relative path to initial default settings file
temp_settings_path = os.getcwd() + '/settings/temp.json' # absolute path to write temp settings file (base + updated) -- will be read in from AirSim during launch
display_windowed = True # True will launch AirSim as a window (recommended) rather than full screen
display_animals = False # True will have animals running around map
self_stabilize = True # True will run custom script to stabilize drone after commands, otherwise can spin out of control -- 
mode_control = Modes.DURATION # how to move drone between points, changes stability (DURATION recommended)
drone_speed = 5 # average linear speed drone will move -- in m/s (recommend 2 for stability)
start_position = [3, 0, 0] # will teleport drone to this position before starting trajectory
positions_list = [ # list of positions for drone to sequentially visit, [x, y, z] in drone coordinates 
    [3, 0, 0],
    [3, 0, -4],
    [10, 10, -6],
    [20, -7, -10],
    [4, -4, -6],
    [4, -2, -4],
    [3, 0, 0],
] # drone coordinates: +x is forward facing from initial drone position, +y is right, +z is downwards
data_types = [ # what type of data to collect at each frame
    Data.TIMESTAMP,
    Data.DRONE_POSITION,
    Data.DRONE_ROTATION,
    Data.DRONE_VELOCITY,
    Data.CAMERA_POSITION,
    Data.CAMERA_ROTATION,
    Data.BGR,
    Data.ROTOR_SPEED,
]

drone_name = "Drone"
camera_name = "FixedCamera"
# camera_view values:
    # 'FixedCamera' defined in settings.json file
    # 'front_center' or '0'
    # 'front_right' or '1'
    # 'front_left' or '2'
    # 'bottom_center' or '3'
    # 'back_center' or '4'

frame_rate =  1 # frames per second to capture data at during trajectory movement higher than 8 are unstable 
collection_time = 30 # number of seconds to collect data for 
smile_for_the_camera = 0 # number of seconds to freeze screen at each frame for debugging/demo purposes -- you can set this to zero for actual data collection

# save above parameters to write to file for future reference
all_local_vars = locals()
user_local_vars = {k:v for k, v in all_local_vars.items() if (not k.startswith('__') and k not in initial_locals and k not in ['initial_locals','all_local_vars'])}
# convert user parameters to json writable dictionary
def convert_params(params_dict):
    out_dict = {}
    for key, value in params_dict.items():
        if isinstance(value, Enum):
            value = value.name
        if isinstance(value, list):
            new_list = []
            for value2 in value:
                if isinstance(value2, Enum):
                    value2 = value2.name
                new_list.append(value2)
            value = new_list
        out_dict[key] = value
    return out_dict
user_params = convert_params(user_local_vars)


## ******** LAUNCH AIRSIM ******** 

# flags to include when launching sh file
flags_list = []
if display_windowed:
    flags_list.append('windowed') # without this flag will be full screen
flags_str = '-' + ' -'.join(flags_list)
# json settings to use for AirSim
# initialize based settings json file to pass in terminal
settings = json.load(open(base_settings_path, 'r'))
# update with additional settings
# settings[key1][key2] = value # example
# write temp json to file for terminal launch
json.dump(settings, open(temp_settings_path, 'w'), indent=2)
# make command to launch airsim
terminal_command = f'sh {release_path} {flags_str} -settings=\"{temp_settings_path}\"'
print('press any key to launch AirSim with command:', terminal_command)
print('After AirSim has properly launched and rendered, then press any key again to continue...')
ini = input()

# launch AirSim
process = subprocess.Popen(terminal_command, shell=True, start_new_session=True)
process_pid = process.pid

try:
    # wait for airsim to fully launch -- user controlled
    # automatically wait 10 seconds
    #time.sleep(10) 
    # manually prompt user for when airsim is launched
    wait = input() 
    
    # establish connection with python API
    client = airsim.MultirotorClient()
    client.enableApiControl(True)
    client.armDisarm(True)
    client.takeoffAsync().join()
    
    # remove moving animals from scene
    if not display_animals:
        objects = client.simListSceneObjects()
        animals = [name for name in objects if 'Deer' in name or 'Raccoon' in name or 'Animal' in name]
        _ = [client.simDestroyObject(name) for name in animals] # PETA has joined the chat
        
    

    ## ******** EXECUTE DRONE MOVEMENT AND DATA COLLECTION ******** 
    
    # helper functions
    # AirSim movement can be unstable: https://github.com/microsoft/AirSim/issues/4780
    # this is a stopgap I wrote to smooth out movement
    def stabilize_drone():
        client.rotateByYawRateAsync(0, 0.001).join()
        client.moveByVelocityAsync(0, 0, 0, 0.001).join()
    # the below "move_by" methods are 3 ways of telling AirSim to move the drone
    # you will only need these if you need to later manually move it
    # each way varies in stability -- 
    # move_by_position can lead to timeout errors
    # move_by_duration is the most stable however less accurate
    # move_by_teleport instantly moves drones to position -- ignoring collisions and very accurate
    def move_by_position(x, y, z):
        if self_stabilize: stabilize_drone(5)
    def move_by_duration(x, y, z):
        if self_stabilize: stabilize_drone()
    def move_by_teleport(x, y, z, pitch=0, roll=0, yaw=0):
        pose = airsim.Pose(
            airsim.Vector3r(x, y, z), 
            airsim.to_quaternion(pitch, roll, yaw),
        )
        client.simSetVehiclePose(pose, ignore_collision=True)
        if self_stabilize: stabilize_drone()
    if mode_control == Modes.POSITION:
        move_func = move_by_position
    if mode_control == Modes.DURATION:
        move_func = move_by_duration
    if mode_control == Modes.TELEPORTATION:
        move_func = move_by_teleport
    
    # spawn drone at start position
    move_by_teleport(*start_position)
    
    # issue command to move drone on path 
    path = [airsim.Vector3r(*position) for position in positions_list]
    move_future = client.moveOnPathAsync(path, velocity=drone_speed) # new thread, continue with code while this executes
    #client.moveOnPathAsync(path, velocity=drone_speed).join() # join will not continue code until this thread is done
    # capture data at given frame rate while drone is moving 
    n_frames = collection_time * frame_rate
    delta_t = collection_time / n_frames
    frames = [] # will contain all data at each frame
    for t in range(n_frames):
        print('frame', t+1)
        client.simPause(True)
        #kinematics = client.getMultirotorState().kinematics_estimated
        #kinematics = client.simGetGroundTruthKinematics()
        #drone_position = kinematics.position  # Vector3r (x,y,z)
        #drone_velocity = kinematics.linear_velocity  # Vector3r (x,y,z)
        #drone_orientation = kinematics.orientation  # Quaternionr (w,x,y,z)
        # move_by_teleport(*drone_position, *np.array(airsim.to_eularian_angles(drone_orientation)))
        # set camera
        #if camera == Camera.GLOBAL:
            #drone_orientation_eularian = np.array(airsim.to_eularian_angles(drone_orientation))
            #global_orientation = np.array([math.radians(theta) for theta in camera_global_orientation])
            #pitch, roll, yaw = global_orientation - drone_orientation_eularian
            #camera_orientation = airsim.to_quaternion(pitch, roll, yaw)
            # camera_position = airsim.Vector3r(*camera_global_position) - drone_position
            # camera_pose = airsim.Pose(camera_position, camera_orientation)
            # client.simSetCameraPose("0", camera_pose) # by default this is forward facing camera on drone, we are overwriting it
        if smile_for_the_camera > 0:
            dummy_response = client.simGetImages([airsim.ImageRequest('0', 0, False, False)])[0]
            #time.sleep(0.1)
            time.sleep(smile_for_the_camera)
        # freeze client and capture data (freeze to ensure all data is synchronized)
        # capture each type of data and save to map for this frame
        data_map = {}
        drone_pose = client.simGetVehiclePose(vehicle_name=drone_name)
        camera_pose = client.simGetCameraInfo(camera_name=camera_name, external=True).pose
        for data_type in data_types:
            if data_type == Data.TIMESTAMP:
                data = t * delta_t
            if data_type == Data.DRONE_POSITION:
                x, y, z = drone_pose.position.x_val, drone_pose.position.y_val, drone_pose.position.z_val
                data = [x, y, z]
            if data_type == Data.DRONE_ROTATION:
                w, x, y, z = drone_pose.orientation.w_val, drone_pose.orientation.x_val, drone_pose.orientation.y_val, drone_pose.orientation.z_val
                data = [w, x, y, z]
            if data_type == Data.CAMERA_POSITION:
                x, y, z = camera_pose.position.x_val, camera_pose.position.y_val, camera_pose.position.z_val
                data = [x, y, z]
            if data_type == Data.CAMERA_ROTATION:
                w, x, y, z = camera_pose.orientation.w_val, camera_pose.orientation.x_val, camera_pose.orientation.y_val, camera_pose.orientation.z_val
                data = [w, x, y, z]
            if data_type == Data.DRONE_VELOCITY:
                drone_velocity = client.getMultirotorState(vehicle_name=drone_name).kinematics_estimated.linear_velocity
                data = [drone_velocity.x_val, drone_velocity.y_val, drone_velocity.z_val]
            if data_type == Data.ROTOR_SPEED:
                multirotor_state = client.getRotorStates(vehicle_name=drone_name)
                data = [rotor for rotor in multirotor_state.rotors]
            if data_type == Data.BGR:
                # image_type values:
                    # Scene = 0, 
                    # DepthPlanar = 1, 
                    # DepthPerspective = 2,
                    # DepthVis = 3, 
                    # DisparityNormalized = 4,
                    # Segmentation = 5,
                    # SurfaceNormals = 6,
                    # Infrared = 7,
                    # OpticalFlow = 8,
                    # OpticalFlowVis = 9
                image_type = airsim.ImageType.Scene
                # this controls dimensions of output img -- either (height, width) for 1-channel or (height, width, channels)
                n_channels = 1
                if image_type == airsim.ImageType.Scene: # I only know the dimensions of Scene and DepthPerspective
                    n_channels = 3 
                as_float = False # BGR returns as uint
                compress = False # do not compress
                requests = [
                    airsim.ImageRequest(camera_name, airsim.ImageType.Scene, as_float, compress)
                ]
                # capture and process given image request
                img_array = []
                while len(img_array) <= 0: # loop for dead images (happens some times)
                    response = client.simGetImages(requests, external=True)[0]
                    if as_float:
                        np_flat = np.array(response.image_data_float, dtype=float)
                    else:
                        np_flat = np.fromstring(response.image_data_uint8, dtype=np.uint8)
                    if n_channels == 1:
                        img_array = np.reshape(np_flat, (response.height, response.width))
                    else:
                        img_array = np.reshape(np_flat, (response.height, response.width, 3))
                data = img_array
            data_map[data_type.name] = data
        frames.append(data_map)
        client.simPause(False)
        # wait till next frame to capture data
        time.sleep(delta_t)
        
    # write all data to file -- including this .py file and user set parameters
    os.makedirs(data_dir, exist_ok=True)
    # copy this python file
    current_file_path = os.path.abspath(__file__)
    python_path = os.path.join(data_dir, 'python.py')
    shutil.copy2(current_file_path, python_path)
    # write user parameters
    params_path = os.path.join(data_dir, 'params.json')
    json.dump(user_params, open(params_path, 'w'), indent=2)
    # write frames data
    frames_path = os.path.join(data_dir, 'frames.p')
    pickle.dump(frames, open(frames_path, 'wb'))
    
    # wait for the trajectory to finish
    move_future.join()

    
finally:
    # always close AirSim process even if stopped with ctrl+c (KeyboardInterrupt)
    parent = psutil.Process(process_pid)
    for child in parent.children(recursive=True):
        child.kill()
    parent.kill()
    
    print('FIN')
