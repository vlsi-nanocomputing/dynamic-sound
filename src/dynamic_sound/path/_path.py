import os
import numpy as np
from scipy.spatial.transform import Rotation, Slerp
from scipy.interpolate import interp1d

class Path:
    def __init__(self, positions=None, *, file=None):
        self.positions = None
        self.duration = 0.0

        if positions is not None:
            self.positions = np.array(positions, dtype=np.float64)
            self.duration = self.positions[-1, 0] - self.positions[0, 0]
        
        if file is not None:
            self.load_path(file)

    def save_path(self, file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        np.savetxt(file_path, self.positions, delimiter=',')

    def load_path(self, file_path):
        self.positions = np.genfromtxt(file_path, delimiter=',', dtype=np.float64)
        self.duration = self.positions[-1][0] - self.positions[0][0]
    
    def get_position(self, time):
        # Ensure time is within range
        if self.positions[0, 0] <= time < self.positions[-1, 0]:

            # Find interval containing `time`
            for i in range(len(self.positions) - 1):
                t0 = self.positions[i, 0]
                t1 = self.positions[i + 1, 0]
                if t0 <= time < t1:
                    # Linear interpolation factor
                    alpha = (time - t0) / (t1 - t0)

                    # --- Position interpolation (linear) ---
                    p0 = self.positions[i, 1:4]
                    p1 = self.positions[i + 1, 1:4]
                    position = p0 + alpha * (p1 - p0)

                    # --- Rotation interpolation (slerp) ---
                    q0 = self.positions[i, 4:8]
                    q1 = self.positions[i + 1, 4:8]
                    
                    q0 /= np.linalg.norm(q0)  # Normalize quaternions to avoid numerical issues
                    q1 /= np.linalg.norm(q1)

                    # Create Rotation objects
                    key_rots = Rotation.from_quat([q0, q1])
                    key_times = [0, 1]

                    # Create Slerp object
                    slerp = Slerp(key_times, key_rots)

                    # Interpolate
                    interp_rot = slerp([alpha])[0]
                    rotation = interp_rot.as_quat()

                    return position, rotation
        
        # If time not in the range
        return None, None

    
    def interpolate_path(self, num_points=50):
        # Split input
        t = self.positions[:, 0]
        pos = self.positions[:, 1:4]
        quat = self.positions[:, 4:8]

        # New uniform time vector
        t_new = np.linspace(t[0], t[-1], num_points)

        # --- Position interpolation ---
        interp_pos = np.zeros((num_points, 3))
        for i in range(3):
            f = interp1d(t, pos[:, i], kind='cubic')
            interp_pos[:, i] = f(t_new)

        # --- Quaternion interpolation ---
        rotations = Rotation.from_quat(quat)
        slerp = Slerp(t, rotations)
        interp_rot = slerp(t_new)
        interp_quat = interp_rot.as_quat()

        # Combine interpolated data
        self.positions = np.column_stack([t_new, interp_pos, interp_quat])

    def plot_path_3d(self, show=True, ax=None, dot_every=1):
        import matplotlib.pyplot as plt

        pos = self.positions[:, 1:4]

        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')

        # Path line
        ax.plot(pos[:, 0], pos[:, 1], pos[:, 2], 'b-', linewidth=1.5, label='Path')

        # Intermediate dots
        ax.scatter(
            pos[::dot_every, 0],
            pos[::dot_every, 1],
            pos[::dot_every, 2],
            color='blue',
            s=10,
            alpha=0.6,
            label='Intermediate points' if dot_every == 1 else None
        )

        # Start and end points
        ax.scatter(pos[0, 0], pos[0, 1], pos[0, 2], color='green', s=60, label='Start', zorder=3)
        ax.scatter(pos[-1, 0], pos[-1, 1], pos[-1, 2], color='red', s=60, label='End', zorder=3)
        
        # Labels and aesthetics
        ax.set_title("3D Path with Intermediate Points")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.legend()
        ax.grid(True)
        ax.view_init(elev=25, azim=-60)  # nicer default 3D view

        if show:
            plt.show()
        return ax


    def plot_quaternion_directions(self, show=True, ax=None, step=10, scale=0.1):
        import matplotlib.pyplot as plt

        pos = self.positions[:, 1:4]
        quat = self.positions[:, 4:8]
        rot = Rotation.from_quat(quat)

        # Subsample
        idx = np.arange(0, len(pos), step)
        p = pos[idx]
        Rm = rot[idx].as_matrix()  # shape (m, 3, 3)

        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')

        # Plot axes for each sampled frame
        for i in range(len(p)):
            origin = p[i]
            R = Rm[i]
            # Each column of R is a local axis in world coordinates
            x_dir, y_dir, z_dir = R[:, 0], R[:, 1], R[:, 2]

            ax.quiver(*origin, *x_dir, length=scale, normalize=True, color='r', linewidth=1.2)
            ax.quiver(*origin, *y_dir, length=scale, normalize=True, color='g', linewidth=1.2)
            ax.quiver(*origin, *z_dir, length=scale, normalize=True, color='b', linewidth=1.2)

        ax.set_title("Quaternion Orientation Axes (X=red, Y=green, Z=blue)")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.grid(True)
        ax.set_box_aspect([1, 1, 1])

        if show:
            plt.show()
        return ax
