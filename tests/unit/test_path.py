import pytest
import os
import sys
import numpy as np

import dynamic_sound as ds

@pytest.fixture
def path_empty():
    return ds.Path()

@pytest.fixture
def path_linear():
    return ds.Path(positions=[
        #time,  x,   y,   z,   qw,  qx,  qy,  qz
        [0.0,   0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
        [1.0,   1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0]
    ])

@pytest.fixture
def path_from_file():
    file_path = os.path.join("tests", "res", "path", "path_2pt.csv")
    return ds.Path(file=file_path)


def test_path_empty(path_empty):
    assert isinstance(path_empty, type(path_empty))
    path = path_empty
    assert path.positions is None
    assert path.duration == 0.0
    assert path.start_time == 0.0

def test_path_linear(path_linear):
    assert isinstance(path_linear, type(path_linear))
    path = path_linear
    assert path.positions.shape == (2, 8)
    assert path.duration == 1.0
    assert path.start_time == 0.0

def test_path_from_file(path_from_file):
    assert isinstance(path_from_file, type(path_from_file))
    path = path_from_file
    assert path.positions.shape == (2, 8)
    assert path.duration == 1.0
    assert path.start_time == 0.0

@pytest.mark.parametrize("start_time, end_time, expected_duration",[
    (0.0, 1.0, 1.0),
    (5.0, 10.0, 5.0),
    (-2.0, 3.0, 5.0),
    (100.5, 101.25, 0.75),
])
def test_path_start_time_and_duration(start_time, end_time, expected_duration):
    path = ds.Path(positions=[
        #time,  x,   y,   z,   qw,  qx,  qy,  qz
        [start_time,   0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
        [end_time,   1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0]
    ])
    assert path.start_time == start_time
    assert path.duration == pytest.approx(expected_duration, rel=1e-12)

def test_save_path(path_from_file):
    file_path = os.path.join("tests", "_tmp", "test_save_path.csv")
    path_from_file.save_path(file_path)
    assert os.path.exists(file_path)
    loaded_positions = np.genfromtxt(file_path, delimiter=',', dtype=np.float64)
    assert np.array_equal(loaded_positions, path_from_file.positions)
    os.remove(file_path)

def test_get_position(path_linear):
    path = path_linear
    time = 0.5
    position, rotation = path.get_position(time)
    assert isinstance(position, np.ndarray)
    assert isinstance(rotation, np.ndarray)
    assert position.shape == (3,)
    assert rotation.shape == (4,)
    assert pytest.approx(position, rel=1e-12) == np.array([0.5, 0.5, 0.5])
    assert pytest.approx(rotation, rel=1e-12) == np.array([1.0, 0.0, 0.0, 0.0])

def test_get_position_out_of_bounds(path_linear):
    path = path_linear
    position, rotation = path.get_position(-1.0)
    assert position is None
    assert rotation is None
    position, rotation = path.get_position(2.0)
    assert position is None
    assert rotation is None

def test_interpolation_accuracy(path_linear):
    path = path_linear
    times_to_test = np.linspace(0.0, 1.0, num=25)
    for time in times_to_test[:-1]:
        position, rotation = path.get_position(time)
        expected_position = np.array([time, time, time])
        expected_rotation = np.array([1.0, 0.0, 0.0, 0.0])
        assert pytest.approx(position, rel=1e-12) == expected_position
        assert pytest.approx(rotation, rel=1e-12) == expected_rotation
    position, rotation = path.get_position(times_to_test[-1])
    assert position is None
    assert rotation is None

def test_path_interpolation_linear(path_linear):
    path = path_linear
    assert path.positions.shape == (2, 8)
    resampling_points = 25
    path.interpolate_path(num_points=resampling_points)
    assert path.positions.shape == (resampling_points, 8)
    expected_positions = np.array([[time, time, time, time, 1.0, 0.0, 0.0, 0.0] for time in np.linspace(0.0, 1.0, num=resampling_points)])
    assert path.positions == pytest.approx(expected_positions, rel=1e-12)

def test_plot_path_3d(path_linear):
    path = path_linear
    try:
        ax = path.plot_path_3d(show=False)
        assert ax is not None
    except Exception as e:
        pytest.fail(f"plot_path_3d raised an exception: {e}")

def test_plot_quaternion_directions(path_linear):
    path = path_linear
    try:
        ax = path.plot_quaternion_directions(show=False)
        assert ax is not None
    except Exception as e:
        pytest.fail(f"plot_quaternion_directions raised an exception: {e}")

