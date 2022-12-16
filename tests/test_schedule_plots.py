"""Test schedule_plots module."""
# %% Imports
from __future__ import annotations

# Third Party Imports
from matplotlib import pyplot as plt

# satvis Imports
from satvis.schedule_plots import padSchedList, plotSchedule

# %% Build data
# building block sets
dat1 = [(2, 2), (6, 3), (10, 5)]
dat2 = [(0, 2), (5, 8)]
dat3 = [(4, 1), (1, 1), (7, 2), (10, 1)]

dat4 = [dat1, dat2, dat3]

dat_a = [(1, 2), (4, 1), (8, 5)]
dat_b = [(0, 4), (4.5, 3)]
dat_c = [(3, 1), (0, 1), (6, 2), (9, 1)]

# multiple sensors, multiple satellites
dat_big = [dat4, [dat_a, dat_b, dat_c]]

dat5 = [[(0, 1)], [(1, 7)], [(8, 6)]]
dat6 = [[(0, 3)], [], [(8, 2)]]
dat_big2 = [dat5, dat6]

dat_empty = [[[], [], []], [[], [], []]]

sensor_labels = ["Sensor A", "Sensor B"]
target_labels = ["Sat 1", "Sat 2", "Sat 3"]

# single sensor, multiple satellite
dat_small = [dat4]
# single satellite, multiple sensors
dat_1sat = [[dat1], [dat2]]
# %% Test pad list
pad = padSchedList(
    dat_1sat,
    [target_labels[0]],
    sensor_labels[:2],
    dat_1sat[1],
    [target_labels[0]],
    [sensor_labels[1]],
)
print(f"superset list=\n{dat_1sat}")
print(f"input list list=\n{dat_1sat[1]}")
print(f"padded list=\n{pad}")

# %% Test Plots
# with no tasked input
print("No tasked inputs")
plt.style.use("default")
f = plt.figure()
f = plotSchedule(dat_big, target_labels, sensor_labels, f)

# with empty tasked input
print("Empty tasked input")
f = plt.figure()
f = plotSchedule(
    dat_big,
    target_labels,
    sensor_labels,
    f,
    dat_empty,
    target_labels,
    sensor_labels,
)

# with populated tasked input
print("populated tasked input")
f = plt.figure()
f = plotSchedule(
    dat_big,
    target_labels,
    sensor_labels,
    f,
    dat_big2,
    target_labels,
    sensor_labels,
)

# with empty availability
print("empty availability")
f = plt.figure()
f = plotSchedule([], target_labels, sensor_labels, f)

# string input for sensor labels
print("string input for sensor labels")
f = plt.figure()
f = plotSchedule(dat_small, target_labels, sensor_labels[0], f)


# one sensor, multiple satellites
print("one sensor, multiple satellites")
f = plt.figure()
f = plotSchedule(dat_small, target_labels, [sensor_labels[0]], f)


# multiple sensors, one satellite
print("multiple sensors, one satellite")
f = plt.figure()
f = plotSchedule(dat_1sat, [target_labels[0]], sensor_labels[:2], f)


# one sensor, one satellite
print("one sensor, one satellite")
f = plt.figure()
f = plotSchedule([dat_1sat[0]], [target_labels[0]], sensor_labels[:1], f)

# one sensor can't see one satellite, other sensor can
avail1 = [[[(2, 1)], [(4, 1)]], [[], [(2, 3)]]]
f = plt.figure()
f = plotSchedule(avail1, ["1", "2"], ["A", "B"], f)


# %% Complicated Inputs
# different num sensors for availability vs tasked
print("different num sensors for  availability vs scheduled")
dat_scheduled = [[[(0, 1), (6, 2)]]]
f = plt.figure()
f = plotSchedule(
    dat_1sat,
    [target_labels[0]],
    sensor_labels[:2],
    f,
    dat_scheduled,
    [target_labels[0]],
    [sensor_labels[1]],
)


# change sensor label
print("different num sensors for  availability vs scheduled (alternate)")
f = plt.figure()
f = plotSchedule(
    dat_1sat,
    [target_labels[0]],
    sensor_labels[:2],
    f,
    dat_scheduled,
    [target_labels[0]],
    [sensor_labels[0]],
)

# %%
print("Schedule has same # of sensors, different satellites")
set_a = [dat1, dat2]
set_tot = [set_a, [dat3, []]]
set_partial = [[dat1], [dat3]]

f = plt.figure()
f = plotSchedule(
    set_tot,
    ["sat1", "sat2"],
    ["sensA", "sensB"],
    f,
    set_partial,
    ["sat1"],
    ["sensA", "sensB"],
)


# %%
plt.show()
print("done")
