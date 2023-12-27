# %% Imports
from __future__ import annotations

# Third Party Imports
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from numpy import array, cos, linspace, ones, sin, stack, zeros

# satvis Imports
from satvis.visibility_func import visDerivative, visibilityFunc

# Test that visDerivative and visibilityFunc are consistent
n = 100
t = linspace(0, 6, num=n)
r1 = stack([ones(n), -1 * ones(n), zeros(n)], axis=1)
r2 = stack((sin(t), cos(t), zeros(n)), axis=1)
r1_dot = stack([zeros(n), zeros(n), zeros(n)], axis=1)
r2_dot = stack((cos(t), sin(t), zeros(n)), axis=1)

vis_history = []
vis_der_history = []
phi_history = []
a1_history = []
a2_history = []
phi_der_history = []
a1_der_history = []
a2_der_history = []

for idx, (i, j, ii, jj) in enumerate(zip(r1, r2, r1_dot, r2_dot)):
    vis, phi, a1, a2 = visibilityFunc(i, j, 0.9, 0)
    vis_der, phi_der, a1_der, a2_der = visDerivative(i, ii, j, jj, a1, a2, phi, 0.9)
    vis_history.append(vis)
    vis_der_history.append(vis_der)
    phi_history.append(phi)
    a1_history.append(a1)
    a2_history.append(a2)
    phi_der_history.append(phi_der)
    a1_der_history.append(a1_der)
    a2_der_history.append(a2_der)

# Plot vis history and vis_der_history
fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, 1)
ax1.plot(range(len(vis_history)), vis_history)
ax1.set_ylabel("Visibility History")
ax2.plot(range(len(vis_der_history)), vis_der_history)
negative_indices = [i for i, value in enumerate(vis_der_history) if value < 0]
negative_values = [value for value in vis_der_history if value < 0]
ax2.scatter(negative_indices, negative_values, color="blue", marker="s")
ax2.set_ylabel("Visibility Derivative History")
ax3.plot(range(len(phi_history)), phi_history)
ax3.set_ylabel("Phi History")
ax4.plot(range(len(phi_der_history)), phi_der_history)
ax4.set_ylabel("Phi der History")
ax5.plot(range(len(a1_der_history)), a1_der_history)
ax5.set_ylabel("a1der History")
ax6.plot(range(len(a2_der_history)), a2_der_history)
ax6.set_ylabel("a2der History")

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
    ax.plot([i[0], j[0]], [i[1], j[1]], "k-")

plt.show()
