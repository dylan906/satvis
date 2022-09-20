"""Test for schedule_tree module"""
# %% Imports
# Standard Library Imports

# Third Party Imports
import matplotlib.pyplot as plt
from numpy import arange, array, empty, shape

# Sat Vis Imports
# from scheduler_testbed.common.utilities import loadJSONFile
from sat_vis.schedule_tree import getRiseSet, getVisHist

# %% Test getVisHist
print("\nTest getVisHist()...")
t1 = [0, 1, 2, 3]
# create dummy state history
states_sats = empty([6, len(t1), 3])
states_sens = empty([6, len(t1), 2])

# Positions must be greater than Earth radius to get through
# visibilityFunc error check. Velocities aren't used so set to zero.
states_sats[3:, :, :] = 0
states_sats[:3, :, 0] = array([8000, 9000, 10000, 11000])
states_sats[:3, :, 1] = -1 * array([8000, 9000, 10000, 11000])
states_sats[:3, :, 2] = -1 * array([8000, 9000, 10000, 11000])
states_sens[3:, :, :] = 0
states_sens[:3, :, 0] = 1.1 * array([8000, 9000, 10000, 11000])
states_sens[:3, :, 1] = -1.1 * array([8000, 9000, 10000, 11000])

# %% Build test data
print("Build test parameters...")
dat1 = [
    {"sat_num": 1, "sat_name": 1, "init_eci": [7000, 0.0, 0.0, 0.0, 7.6, 0.0]},
    {"sat_num": 2, "sat_name": 2, "init_eci": [7200, 0.0, 0.0, 0.0, -7.5, 0.0]},
    {"sat_num": 3, "sat_name": 3, "init_eci": [7400, 0.0, 0.0, 0.0, 7.4, 0.0]},
    {"id": "A", "lat": 0, "lon": 0, "alt": 0},
    {"id": "B", "lat": 0, "lon": 0.1, "alt": 0},
]

dat_sat = dat1[:3]
dat_sens = dat1[3:]

num_sats = len(dat_sat)
num_sens = len(dat_sens)

print(f"num_sats = {num_sats}")
print(f"num_sens = {num_sens}")
print(f"dat_sat = \n{dat_sat}")
print(f"dat_sens = \n{dat_sens}")

[tree, vis] = getVisHist(dat_sat, dat_sens, states_sats, states_sens, t1)
print(f"tree = \n{tree}")
print(f"visibility hist = \n{vis}")
print(f"shape(vis) = {shape(vis)}")

# %% Test getRiseSet
print("\nTest getRiseSet()...")

# initial time (s)
t0 = 0
# final time (s)
tf = 40 * 60
# number of steps in simulation
numStep = 10
# time step
dt = tf / numStep

# time vector
t = arange(t0, tf, dt)

[sched_tree, v, x_sens, x_sat] = getRiseSet(dat_sat, dat_sens, t)

print(f"len(sched_tree.sched_tree) = {len(sched_tree.sched_tree)}")
print(f"sched_tree.num_sats = {sched_tree.num_targs}")
print(f"sched_tree.num_sens = {sched_tree.num_sens}")
print(f"sched_tree.sat_list = {sched_tree.targ_list}")
print(f"sched_tree.sens_list = {sched_tree.sens_list}")

# Plot visibility and state history
plt.style.use("default")
fig, ax = plt.subplots(3)
for i, d_ssn in enumerate(dat_sens):
    for j, d_sat in enumerate(dat_sat):
        ax[0].plot(t, v[i, j, :], marker=".")
ax[0].set_ylabel("V")
ax[0].set_xlabel("t")
for i in range(num_sats):
    ax[1].plot(x_sat[0, :, i], x_sat[1, :, i], marker=".")
ax[1].set_title("sats")
ax[1].set_xlabel("I")
ax[1].set_ylabel("J")
for i in range(num_sens):
    ax[2].plot(x_sens[0, :, i], x_sens[1, :, i], marker=".")
ax[2].set_title("sensors")
ax[2].set_xlabel("I")
ax[2].set_ylabel("J")
plt.tight_layout()

# %% Test Schedule Class
for i in range(len(sched_tree.sched_tree)):
    print(f"Interval[{i}] = {list(sched_tree.sched_tree)[i]}")
    print(f"Sat Name[{i}] = {sched_tree.getTargAtInt(i)}")
    print(f"Sens Name[{i}] = {sched_tree.getSensAtInt(i)}")

print(f"sched_tree.getTargAtInt(0) = {sched_tree.getTargAtInt(0)}")
print(f"sched_tree.getTargAtInt(1) = {sched_tree.getTargAtInt(1)}")
print(f"sched_tree.getSensAtInt(0) = {sched_tree.getSensAtInt(0)}")

print(f"sched_tree.getTargs(100) = {sched_tree.getTargs(100)}")
print(f"sched_tree.getSens(100) = {sched_tree.getSens(100)}")

print(f"isVis: {sched_tree.isVis(0, 40002, 10001)}")
print(f"isVis: {sched_tree.isVis(2000, 40002, 10001)}")

# %%
plt.show()
print("done")
