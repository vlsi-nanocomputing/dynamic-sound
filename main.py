import os
import dynamic_sound as ds

res_path = os.path.join("examples", "resources")
microphone_sample_rate = 100
source_sample_rate = 100


sim = ds.Simulation(temperature=20, pressure=1, relative_humidity=50)
mic_path = ds.Path(file=os.path.join(res_path, "paths", "camera_path.csv"))
sim.add_microphone(path=mic_path, microphone=ds.microphones.MicrophoneArray(positions=[
                    [0.0, 0.0, 0.0,        0.0, 0.0, 0.0, 0.0]
        ], file_path="tests/_tmp/airsim_path_drone_sound.wav", sample_rate=microphone_sample_rate)
)

drone_sound = ds.sources.AudioFile(filename=os.path.join(res_path, "sounds", "flying_drone.wav"), sample_rate=source_sample_rate, gain_db=10.0, loop=True)
drone_path = ds.Path(file=os.path.join(res_path, "paths", "drone_path.csv"))
sim.add_source(path=drone_path, source=drone_sound)
drone_path.positions[:,3] = -drone_path.positions[:,3]
sim.add_source(path=drone_path, source=drone_sound)
sim.run()

