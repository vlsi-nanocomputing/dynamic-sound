import dynamic_sound as ds
import librosa
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
import numpy as np

filename = "_tmp/directivity_src.wav"

# simulation environment
sim = ds.Simulation(
    temperature=20,
    pressure=1,
    relative_humidity=50
)

# microphone
directivity = ds.microphones.DirectivityType.CARDIOID
positions_deg = range(0, 360, 10)
z_rotation_mic_deg = 45
rotation = R.from_euler('z', z_rotation_mic_deg, degrees=True).as_quat(scalar_first=True)

sim.add_microphone(
    path=ds.Path([
        [0.1,  0.0, 0.0, 0.0,   rotation[0], rotation[1], rotation[2], rotation[3]],
        [0.2,  0.0, 0.0, 0.0,   rotation[0], rotation[1], rotation[2], rotation[3]]
    ]),
    microphone=ds.microphones.MicrophoneArray(
        file_path=filename,
        positions=[(0.0, 0.0, 0.0,  1, 0, 0, 0)],
        sample_rate=8_000,
        directivity=directivity
    )
)



# source
z_rotation_deg_list = range(0, 360, 10)
max_val_for_each_channel = []
for index, z_rotation_deg in enumerate(z_rotation_deg_list):

    sim.remove_sources()
    sim.add_source(
        path=ds.Path([
            [0.0, 200 * np.cos(np.deg2rad(z_rotation_deg)), 200 * np.sin(np.deg2rad(z_rotation_deg)), 0.0,   1, 0, 0, 0],
            [10.0, 200 * np.cos(np.deg2rad(z_rotation_deg)), 200 * np.sin(np.deg2rad(z_rotation_deg)), 0.0,   1, 0, 0, 0]
        ]),
        source=ds.sources.SineWave(
            frequency=440,
            amplitude=1,
            directivity=ds.sources.DirectivityType.OMNIDIRECTIONAL)
    )

    sim.run()


    signal, sr = librosa.load(filename, sr=None, mono=True)
    if sr != 8_000:
        raise ValueError(f"Expected sample rate of 8_000, but got {sr}")

    max_val_for_each_channel.append(np.max(np.abs(signal)))



theta_deg = range(0, 360, 1)
cardioid = [ds.acoustics.attenuations.directivity(np.deg2rad(theta - z_rotation_mic_deg), directivity) for theta in theta_deg]

color_list = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
lower_gain = -20        
plt.figure(figsize=(10, 6))
ax = plt.subplot(111, projection='polar')
ax.scatter(np.deg2rad(positions_deg), 20*np.log10(max_val_for_each_channel), marker='o', label='simulation', color=color_list[1])
ax.plot(np.deg2rad(theta_deg), 20*np.log10(cardioid), label='theory', color=color_list[0])
ax.annotate(
    text="",
    xytext=(np.deg2rad(z_rotation_mic_deg), -5),
    xy=(np.deg2rad(z_rotation_mic_deg), lower_gain),
    arrowprops=dict(arrowstyle="<-", color=color_list[3], linewidth=2, mutation_scale=10),
    annotation_clip=False,
)

ax.grid(True)
plt.legend()
plt.ylim([lower_gain, 0])
ax.yaxis.set_ticks(np.arange(start=lower_gain, stop=5, step=5))
plt.show()