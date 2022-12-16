"""Test for vis_history.py module."""
# %% Imports
# Third Party Imports
from numpy import array, zeros

# satvis Imports
from satvis.vis_history import getVisHist

# %% Test getVisHist
print("\nTest getVisHist()...")
RE = 6371  # km

# time vector
t1 = [0, 1, 2, 3]
# create dummy target/sensor dicts
target_dicts = [
    {"id": 1},
    {"id": 2},
    {"id": 3},
]
sensor_dicts = [
    {"id": "A"},
    {"id": "B"},
]
# create dummy state history
states_targets = zeros([len(t1), 6, 3])
states_sensors = zeros([len(t1), 6, 2])

# Build state histories for the following:
# Visible to each other:
#   # Target 1 / Sensor A
#   # Target 2 / Sensor B
#   # Target 3 / Sensor B
# Not visible to each other:
#   # Target 1 / Sensor B
#   # Target 2 / Sensor A
#   # Target 3 / Sensor A

# Positions must be greater than Earth radius to get through
# visibilityFunc error check. Velocities aren't used so set to zero.
states_targets[:, 0, 0] = array([8000, 9000, 10000, 11000])
states_targets[:, 0, 1] = -1 * array([8000, 9000, 10000, 11000])
states_targets[:, 0, 2] = -1 * array([8000, 9000, 10000, 11000])

states_sensors[:, 0, 0] = 1.1 * array([8000, 9000, 10000, 11000])
states_sensors[:, 0, 1] = -1.1 * array([8000, 9000, 10000, 11000])

tree, v = getVisHist(
    target_dicts,
    sensor_dicts,
    states_targets,
    states_sensors,
    t1,
    RE,
)
print(f"tree = {tree}")
print(f"visibility = \n{v}")
