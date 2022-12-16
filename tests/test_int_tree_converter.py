"""Tests for int_tree_converter module."""
# %% Imports
from __future__ import annotations

# Third Party Imports
import matplotlib.pyplot as plt
from intervaltree import Interval, IntervalTree
from numpy import shape

# satvis Imports
from satvis.int_tree_converter import intTree2WindowList
from satvis.schedule_plots import plotSchedule

# %% Create ScheduleTree()
ivs1 = [(1, 2), (4, 7), (8, 9)]
tree1 = IntervalTree(
    Interval(begin, end, {"target_id": "Sat 1", "sensor_id": "Sens A"})
    for begin, end in ivs1
)
ivs2 = [(4, 6), (8, 11)]
tree2 = IntervalTree(
    Interval(begin, end, {"target_id": "Sat 1", "sensor_id": "Sens B"})
    for begin, end in ivs2
)
tree_merged = tree1 | tree2


# %% Test Converter, simple case
print("\nSimple tests:")

[avail, id_sensors, id_targets] = intTree2WindowList(tree_merged)

print(f"avail = \n{avail}")
print(f"shape(avail) ={shape(avail)}")

# Plot
plt.style.use("default")
fig = plt.figure()
plotSchedule(
    availability=avail,
    target_labels=id_targets,
    sensor_labels=id_sensors,
    fig=fig,
)

# %% Test converter, with single sensor/target
print("\nSingle sensor tests:")
print(f"unavalable sched tree=\n{tree1}")
avail1, id_sensors, id_targets = intTree2WindowList(tree1)
print(f"avail = \n{avail1}")
print(f"shape(avail) ={shape(avail1)}")

# Plot
fig = plt.figure()
plotSchedule(
    availability=avail1,
    target_labels=id_targets,
    sensor_labels=id_sensors,
    fig=fig,
)
# %%
plt.show()
print("done")
