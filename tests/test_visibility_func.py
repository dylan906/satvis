"""Tests for `visibility_func.py`."""
# %% Imports
from __future__ import annotations

# Third Party Imports
from matplotlib import pyplot as plt
from numpy import arange, array, linspace, sin, zeros

# satvis Imports
from satvis.visibility_func import visibilityFunc, zeroCrossingFit

# %% Test visibilityFunc
print("\n visibilityFunc simple tests...")
RE = 6378
hg = 0
r1 = array([[RE + 400, 0, 0]]).transpose()
r2 = array([[RE, 0, 0]]).transpose()

[v, phi, a1, a2] = visibilityFunc(r1, r2, RE, hg)
print("phi = " + str(phi))
print("type(phi) = " + str(type(phi)))
print("v = " + str(v))
print(f"type(r1) = {type(r1)}")

r1 = array([[1000, 0, 0]]).transpose()
r2 = array([[2000, 0, 0]]).transpose()
[v, phi, a1, a2] = visibilityFunc(r1, r2, 1000, 0)
print(v)
# %% Warning tests
print("\n visibilityFunc warning tests...")
# Check for object being slightly below surface of Earth-- numerically assume
# object is on surface.
r1_alt = array([6378.136299999999, 0, 0])
r2_alt = array([0, 6378.136299999999, 0])
visibilityFunc(r1_alt, r2_alt, 6378.1363, 0)

# Input object below surface of Earth, should display a warning
r1_alt = array([RE - 0.1, 0, 0])
r2_alt = array([0, RE, 0])
[v, phi, a1, a2] = visibilityFunc(r1_alt, r2_alt, RE, 0)
print(f"v = {v}, phi={phi}, alpha1={a1}, alpha2={a2}")

r1_alt = array([RE, 0, 0])
r2_alt = array([0, RE - 0.1, 0])
[v, phi, a1, a2] = visibilityFunc(r1_alt, r2_alt, RE, 0)
print(f"v = {v}, phi={phi}, alpha1={a1}, alpha2={a2}")

# %% Specific bug point tests
print("\n Point tests...")
# these inputs found to have errors previously, so run check to ensure bug was
# fixed.
r1 = array([[8800, 8800, 8800]]).transpose()
r2 = array([[-8000, -8000, -8000]]).transpose()
visibilityFunc(r1, r2, 6378, 0)

r1 = array([[41569.73845258, 6711.91401374, 0]]).transpose()
r2 = array([[41569.73845258, 6711.91401374, 0]]).transpose()

v, phi, alpha1, alpha2 = visibilityFunc(r1, r2, 6371, 0)

print(v)
# %% Test zeroCrossingFit
print("Test zeroCrossingFit...\n")
plt.style.use("default")

# test special cases
t = array([0, 1, 2, 3, 4])
# no visibility window
vis1 = array([-1, -0.9, -0.8, -0.01, -0.1])
[crossings, riseSet, visTree] = zeroCrossingFit(vis1, t, "der")
print("\n No vis windows")
print(f"crossings={crossings} \nriseSet={riseSet}")
print(f"tree={visTree}")

[fig, ax] = plt.subplots()
ax.plot(crossings, zeros(len(crossings)), marker="*", linestyle="None")
ax.plot(crossings, riseSet, marker="|", linestyle="None")
ax.plot(t, vis1)
ax.set_title("No visibility windows")

# visible for whole series
vis2 = -1 * vis1
[crossings, riseSet, visTree] = zeroCrossingFit(vis2, t, "der")
print("\n visibile for whole series")
print(f"crossings={crossings} \nriseSet={riseSet}")
print(f"tree={visTree}")

[fig, ax] = plt.subplots()
ax.plot(crossings, zeros(len(crossings)), marker="*", linestyle="None")
ax.plot(crossings, riseSet, marker="|", linestyle="None")
ax.plot(t, vis2)
ax.set_title("visible for whole series")

# 0-crossing, ends visible
vis3 = array([-1, -0.1, 0.5, 4, 2])
[crossings, riseSet, visTree] = zeroCrossingFit(vis3, t, "der")
print("\n ends visible")
print(f"crossings={crossings} \nriseSet={riseSet}")
print(f"tree={visTree}")

[fig, ax] = plt.subplots()
ax.plot(crossings, zeros(len(crossings)), marker="*", linestyle="None")
ax.plot(crossings, riseSet, marker="|", linestyle="None")
ax.plot(t, vis3)
ax.set_title("w/ 0-crossings, ends visible")


# 0-crossing, ends not visible
vis4 = array([1, 0.1, -0.5, -4, -2])
[crossings, riseSet, visTree] = zeroCrossingFit(vis4, t, "der")
print("\n ends not visible")
print(f"crossings={crossings} \nriseSet={riseSet}")
print(f"tree={visTree}")

[fig, ax] = plt.subplots()
ax.plot(crossings, zeros(len(crossings)), marker="*", linestyle="None")
ax.plot(crossings, riseSet, marker="|", linestyle="None")
ax.plot(t, vis4)
ax.set_title("w/ 0-crossings, ends not-visible")


# starts stradling 0 (-++++)
vis_a = array([-1, 0.2, 0.5, 4, 2])
[crossings, riseSet, visTree] = zeroCrossingFit(vis_a, t, "der")
print("\n straddle, start negative (-++++)")
print(f"crossings={crossings} \nriseSet={riseSet}")
print(f"tree={visTree}")

[fig, ax] = plt.subplots()
ax.plot(crossings, zeros(len(crossings)), marker="*", linestyle="None")
ax.plot(crossings, riseSet, marker="|", linestyle="None")
ax.plot(t, vis_a)
ax.set_title("starts stradling 0 (-++++)")


# starts stradling 0 (+----)
vis_a = array([1, -0.2, -0.5, -4, -2])
[crossings, riseSet, visTree] = zeroCrossingFit(vis_a, t, "der")
print("\n straddle, start positive (+----)")
print(f"crossings={crossings} \nriseSet={riseSet}")
print(f"tree={visTree}")

[fig, ax] = plt.subplots()
ax.plot(crossings, zeros(len(crossings)), marker="*", linestyle="None")
ax.plot(crossings, riseSet, marker="|", linestyle="None")
ax.plot(t, vis_a)
ax.set_title("starts stradling 0 (+----)")


# starts stradling 0 (--+++)
vis_a = array([-1, -0.2, 0.5, 4, 2])
[crossings, riseSet, visTree] = zeroCrossingFit(vis_a, t, "der")
print("\n straddle, start negative (--+++)")
print(f"crossings={crossings} \nriseSet={riseSet}")
print(f"tree={visTree}")

[fig, ax] = plt.subplots()
ax.plot(crossings, zeros(len(crossings)), marker="*", linestyle="None")
ax.plot(crossings, riseSet, marker="|", linestyle="None")
ax.plot(t, vis_a)
ax.set_title("starts stradling 0 (--++++)")

# Double-crossing in a window down-up  (+-+++)
vis_a = array([1, -0.2, 0.5, 4, 2])
[crossings, riseSet, visTree] = zeroCrossingFit(vis_a, t, "der")
print("\n double crossing (+-+++)")
print(f"crossings={crossings} \nriseSet={riseSet}")
print(f"tree={visTree}")

# Double-crossing in a window up-down (-+---)
vis_a = array([-1, 0.2, -0.5, -4, -2])
[crossings, riseSet, visTree] = zeroCrossingFit(vis_a, t, "der")
print("\n double crossing (-+---)")
print(f"crossings={crossings} \nriseSet={riseSet}")
print(f"tree={visTree}")

# Triple-crossing in a window down-up-down  (+-+--)
vis_a = array([1, -0.2, 0.5, -4, -2])
[crossings, riseSet, visTree] = zeroCrossingFit(vis_a, t, "der")
print("\n triple crossing (+-+--)")
print(f"crossings={crossings} \nriseSet={riseSet}")
print(f"tree={visTree}")

# Triple-crossing in a window up-down-up  (-+-++)
vis_a = array([-1, 0.2, -0.5, 4, 2])
[crossings, riseSet, visTree] = zeroCrossingFit(vis_a, t, "der")
print("\n triple crossing (-+-++)")
print(f"crossings={crossings} \nriseSet={riseSet}")
print(f"tree={visTree}")

# More than 1 frame, double-crossing, up-down (...-+--)
vis_a = array([-1, -1, -1, -1, -0.2, +0.5, -4, -2])
t = arange(0, len(vis_a))
[crossings, riseSet, visTree] = zeroCrossingFit(vis_a, t, "der")
print("\n >1 frame, double-crossing (...-+--)")
print(f"crossings={crossings} \nriseSet={riseSet}")
print(f"tree={visTree}")

# More than 1 frame, double-crossing, down-up (...+-++)
vis_a = array([1, 1, 1, 1, 0.2, -0.5, 4, 2])
t = arange(0, len(vis_a))
[crossings, riseSet, visTree] = zeroCrossingFit(vis_a, t, "der")
print("\n >1 frame, double-crossing (...+-++)")
print(f"crossings={crossings} \nriseSet={riseSet}")
print(f"tree={visTree}")


# %% Long time vector
print("\nLong tests \n")
tLong = linspace(0, 30, num=100)
# multiple crossings, ends not visible
vis5 = sin(tLong)
[crossings, riseSet, visTree] = zeroCrossingFit(vis5, tLong, "der")
print("\n Multiple crossings, ends not visible")
print(f"crossings={crossings} \nriseSet={riseSet}")
print(f"tree={visTree}")

[fig, ax] = plt.subplots()
ax.plot(crossings, zeros(len(crossings)), marker="*", linestyle="None")
ax.plot(crossings, riseSet, marker="|", linestyle="None")
ax.plot(tLong, vis5)
ax.set_title("multiple crossings, ends not-visible")


# multiple crossings, ends visible
vis6 = -sin(tLong)
[crossings, riseSet, visTree] = zeroCrossingFit(vis6, tLong, "der")
print("\n Multiple crossings, ends visible")
print(f"crossings={crossings} \nriseSet={riseSet}")
print(f"tree={visTree}")

[fig, ax] = plt.subplots()
ax.plot(crossings, zeros(len(crossings)), marker="*", linestyle="None")
ax.plot(crossings, riseSet, marker="|", linestyle="None")
ax.plot(tLong, vis6)
ax.set_title("multiple crossings, ends visible")

# %%
# Check IntervalTree
vis7 = array([-1, -3, -4, -5, -6])
[crossings3, riseSet3, visTree3] = zeroCrossingFit(
    vis7,
    linspace(0, 5, num=5),
    "hey",
)
print(visTree3)

# %% README Example
print("\n Readme example...")
t = array([0, 1, 2, 3, 4])  # time vector
vis1 = array([-1, -0.1, 0.5, 4, 2])
vis2 = array([-2, -1, -0.5, 1, 1.1])
[_, _, vis_tree1] = zeroCrossingFit(vis1, t, "pair1")
[_, _, vis_tree2] = zeroCrossingFit(vis2, t, "pair2")
combined_tree = vis_tree1 | vis_tree2
print(vis_tree1)
print(vis_tree2)
print(combined_tree)
# %%
plt.show()

print("done")
