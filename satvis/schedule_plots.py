"""Schedule plots module."""
# %% Imports
from __future__ import annotations

# Standard Library Imports
import warnings

# Third Party Imports
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from matplotlib.figure import Figure
from numpy import empty


# %% Main Function
def plotSchedule(
    availability: list[list[list[tuple[float]]]],
    target_labels: list[str],
    sensor_labels: list[str],
    fig: Figure,
    scheduled: list[list[list[tuple]]] = None,
    scheduled_targ_labels: list[str] = None,
    scheduled_sensor_labels: list[str] = None,
) -> Figure:
    """Generates schedule availability plot for N targets and M sensors.

    Args:
        availability (`list[list[list[tuple[float]]]]`): [M[N[d]]] 3-deep
            nested `list`. The lowest level contains a `tuple` of two `floats`
            representing the start time and duration, respectively, of an availability
            window. N must be the same for every M (all 1st-level nested lists
            must be the same length). d does not need to be the same value for
            every N (2nd-level nested lists don't need to be the same length).
        target_labels (`list[str]`): N-long list of target names.
        sensor_labels (`list[str]`): M-long list of sensor names.
        fig (`Figure`): A matplotlib `Figure`.
        scheduled (`list`): (Optional) Same format as availability. Defaults
            to `None`.
        scheduled_targ_labels (`list[str]`): (Optional) Q-long list of
            strings of target names. Must be a subset of entries in
            `target_labels`. Q >= N.
        scheduled_sensor_labels (`list[str]`): (Optional) P-long list of
            strings of sensor names. Must be a subset of entries in
            `sensor_labels`. P >= M.

    Returns:
        `Figure`: Schedule availability plot as a `broken_barh` plot
            from matplotlib. Colored blocks are the data from 'availability',
            black bars are the data from 'scheduled'.

    Notation:
        M = number of sensors
        N = number of targets
        P = number of scheduled sensors
        Q = number of scheduled targets
        d = the number of access windows for a sensor-target per

    Notes:
       If `scheduled` is not `None`, then `scheduled_targ_labels` and
        `scheduled_sensor_labels` are required.

    Example Usage:
        f = plt.figure()
        avail = [
                 [[(2, 1)], [(4, 1)]],  # access windows for Sensor A
                 [[], [(2, 3)]]  #  access windows for Sensor B
                ]
        target_labels = ['1', '2']
        sensor_labels = ['A', 'B']
        f = plotSchedule(avail, target_labels, sensor_labels, f)
        plt.show()

    """
    # Warnings
    if availability == []:
        warnings.warn("No schedule availability. Plot not generated. ")
        return

    if type(target_labels) != list:
        warnings.warn("target_labels must be a list")
        return

    if type(sensor_labels) != list:
        warnings.warn("sensor_labels must be a list")
        return

    # Generate schedule availability (colored) bars
    fig = genPlot(availability, target_labels, sensor_labels, fig, "wide", None, None)

    # Generate scheduled (black) bars
    if scheduled is not None:
        # pad scheduled list with empty lists to be same dimensions as availability list
        padded_sched = padSchedList(
            availability,
            target_labels,
            sensor_labels,
            scheduled,
            scheduled_targ_labels,
            scheduled_sensor_labels,
        )

        fig = genPlot(
            padded_sched,
            target_labels,
            sensor_labels,
            fig,
            "thin",
            scheduled_targ_labels,
            scheduled_sensor_labels,
        )

    return fig


# %% Supporting Functions
def padSchedList(
    super_list: list[list[list[tuple]]],
    super_targs: list[str],
    super_sens: list[str],
    small_list: list[list[list[tuple]]],
    small_targs: list[str],
    small_sens: list[str],
) -> list[list[list[tuple]]]:
    """Pads `small_list` to be same dimensions as `super_list`.

    Args:
        super_list (`list[list[list[tuple]]]`): Availability.
        super_targs (`list[str]`): Names of all targets in `super_list`.
        super_sens (`list[str]`): Names of all sensors in `super_list`.
        small_list (`list[list[list[tuple]]]`): Scheduled.
        small_targs (`list[str]`): Names of all targets in `small_list`.
        small_sens (`list[str]`): Names of all sensors in `small_list`.

    Returns:
        `list[list[list[tuple]]]`: Same dimensions as `super_list`, but with
            contents of `small_list` corresponding to specified targets and
            sensors. Entries corresponding to targets/sensors not included
            in `small_list` are empty lists.
    """
    padded_list = [[] for x in range(len(super_list))]
    index_small = 0
    for i, (sens, dat) in enumerate(zip(super_sens, super_list)):
        # print(i, sens, dat)
        if sens in small_sens:
            padded_list[i] = small_list[index_small]
            index_small += 1
        # print(padded_list)

    return padded_list


def genPlot(
    dat: list[list[list[tuple[float]]]],
    target_labels: list[str],
    sensor_labels: list[str],
    fig: Figure,
    flag: str,
    sched_targ_labels: list[str],
    sched_sensor_labels: list[str],
):
    """Workhorse function for plotSchedule(). Generates broken_barh plots.

    Args:
        dat (`list[list[list[tuple[float]]]]`): [M[N[d]]] 3-deep
            nested `list`. The lowest level contains a `tuple` of two `floats`
            representing the start time and duration, respectively, of an availability
            window. N must be the same for every M (all 1st-level nested lists
            must be the same length). d does not need to be the same value for
            every N (2nd-level nested lists don't need to be the same length).
        target_labels (`list[str]`): N-long list of target names.
        sensor_labels (`list[str]`): M-long list of sensor names.
        fig (`Figure`): matplotlib `Figure`.
        flag (`str`): 'wide' or 'thin' to set whether to create wide colored
            bars or thin black bars.
        sched_targ_labels (`list[str]`): Q-long list of
            strings of target names. Must be a subset of entries in
            `target_labels`. Q must be less than N.
        sched_sensor_labels (`list[str]`): P-long list of
            strings of sensor names. Must be a subset of entries in
            `sensor_labels`. P must be less than M.

    Returns:
        `Figure`: Matplolib broken_hbar plot of access windows.
    """
    # pick any colormap
    cm = get_cmap(name="gist_rainbow")

    # number of sets (number of sensors)
    num_sensors = len(sensor_labels)

    # number boxes per set (number of targets)
    num_targets = len(target_labels)

    # bar widths
    w_big = 1
    w_small = w_big / num_targets
    w_vsmall = w_small / 2

    # bar y-offsets
    y_big = 1.5 * w_big
    y_small = w_big / num_targets
    y_vec = empty([num_sensors])

    # set values depending on wide/thin flag
    if flag == "wide":
        # add subfigure to empty figure
        ax = fig.add_subplot(1, 1, 1)

        # extra offset multiplier
        x = 0

        # alpha value (transparency for plot)
        al = 0.5

        # width of a set of bars associated with one sensor
        w_set = w_big / num_targets

        def chooseCol(i):
            return cm(i / num_targets)

    elif flag == "thin":
        # black bars must be overlaid on colored bars (no stand-alone black
        #   bars)
        ax = plt.gca()
        x = 1
        al = 1
        w_set = 0.5 * (w_big / num_targets)

        def chooseCol(i):
            return "black"

    # loop through y-axis (sensors)
    for j, sens in enumerate(sensor_labels):
        # set y-offset per grouping of bars
        y_offset = y_big * j + x * (w_vsmall / 2)

        # save y-offset value for plotting
        y_vec[j] = y_offset

        # loop through each color bar
        for i, targ in enumerate(target_labels):
            if flag == "wide":
                plt.broken_barh(
                    dat[j][i],
                    (y_offset + (i * y_small), w_set),
                    facecolor=chooseCol(i),
                    edgecolor="black",
                    alpha=al,
                )
            elif (
                (flag == "thin")
                and (sens in sched_sensor_labels)
                and (targ in sched_targ_labels)
            ):
                plt.broken_barh(
                    dat[j][i],
                    (y_offset + (i * y_small), w_set),
                    facecolor=chooseCol(i),
                    edgecolor="black",
                    alpha=al,
                )

    ax.set_yticks(y_vec + w_big / 2)
    ax.set_yticklabels(sensor_labels)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Sensor ID")
    ax.set_title("Schedule Availability")
    leg1 = plt.legend(target_labels, title="Target ID", loc=1)
    ax.add_artist(leg1)
    if flag == "thin":
        black_patch = mpatches.Patch(color="black", label="Scheduled")
        leg2 = plt.legend(handles=[black_patch], loc=4)
        ax.add_artist(leg2)

    return fig
