# %% Imports
from __future__ import annotations

# Third Party Imports
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from numpy import array, cos, diff, linspace, ones, pi, sin, stack, zeros

# satvis Imports
from satvis.visibility_func import (
    _simpleVisibilityFunc,
    visDerivative,
    visibilityFunc,
)

# Test that visDerivative and visibilityFunc are consistent
n = 50
t = linspace(0, 3 * pi / 2 + 0.1, num=n)
r1 = stack([1.0 * ones(n), zeros(n), zeros(n)], axis=1)
r2 = stack((sin(t), cos(t), zeros(n)), axis=1)
r1_dot = stack([zeros(n), zeros(n), zeros(n)], axis=1)
# r2_dot = diff(r2, axis=0)
# r2_dot = stack([zeros(n), zeros(n), zeros(n)], axis=1)
r2_dot = stack((cos(t), sin(t), zeros(n)), axis=1)
r1_mag_dot = zeros(n)
r2_mag_dot = zeros(n)

vis_history = []
vis_der_history = []
phi_history = []
a1_history = []
a2_history = []
phi_der_history = []
a1_der_history = []
a2_der_history = []
c0_history = []
c1_history = []
c2_history = []

for idx, (i, j, ii, jj, iii, jjj) in enumerate(
    zip(r1, r2, r1_dot, r2_dot, r1_mag_dot, r2_mag_dot)
):
    vis, phi, a1, a2 = _simpleVisibilityFunc(i, j, 0.9, 0)
    vis_der, phi_der, a1_der, a2_der, c0, c1, c2 = visDerivative(
        r1=i,
        r1dot=ii,
        r1mag_dot=iii,
        r2=j,
        r2dot=jj,
        r2mag_dot=jjj,
        a1=a1,
        a2=a2,
        phi=phi,
        RE=0.9,
    )
    vis_history.append(vis)
    vis_der_history.append(vis_der)
    phi_history.append(phi)
    a1_history.append(a1)
    a2_history.append(a2)
    phi_der_history.append(phi_der)
    a1_der_history.append(a1_der)
    a2_der_history.append(a2_der)
    c0_history.append(c0)
    c1_history.append(c1)
    c2_history.append(c2)

vis_hist_diff = diff(vis_history)

# # Plot vis history and vis_der_history
# Create a list of data and labels
data = [
    vis_history,
    vis_der_history,
    phi_history,
    phi_der_history,
    a1_history,
    a1_der_history,
    a2_history,
    a2_der_history,
    c0_history,
    c1_history,
    c2_history,
    # vis_hist_diff,
]
labels = [
    "Visibility History",
    "Visibility Derivative History",
    "Phi History",
    "Phi der History",
    "a1 History",
    "a1der History",
    "a2 History",
    "a2der History",
    "c0 History",
    "c1 History",
    "c2 History",
    # "vis_hist_diff",
]

fig, axs = plt.subplots(4, 3)

for i, (d, label) in enumerate(zip(data, labels)):
    row = i // 3
    col = i % 3
    axs[row, col].plot(range(len(d)), d)
    axs[row, col].set_ylabel(label)

    # Add blue squares for negative values in vis_der_history
    if label in ["Visibility Derivative History", "Phi der History", "c0 History"]:
        negative_indices = [j for j, value in enumerate(d) if value < 0]
        negative_values = [value for value in d if value < 0]
        axs[row, col].scatter(
            negative_indices, negative_values, color="blue", marker="s"
        )

# plt.tight_layout()

# plot r1 and r2 in 2d space
fig, ax = plt.subplots()
r1_arr = array(r1)
r2_arr = array(r2)
ax.plot(r1_arr[:, 0], r1_arr[:, 1], "o")
ax.plot(r2_arr[:, 0], r2_arr[:, 1], "x")
# Create a circle with radius 0.9 centered at (0, 0)
circle = patches.Circle((0, 0), 0.9, fill=False)
# Add the circle to the ax1
ax.add_patch(circle)
for i, j in zip(r1, r2):
    # ax.plot([i[0], j[0]], [i[1], j[1]], "k-")
    ax.plot([0, i[0]], [0, i[1]], "k-")
    ax.plot([0, j[0]], [0, j[1]], "k-")

plt.show()
