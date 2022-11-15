"""Interval Tree Converter module.

Converts list of IntervalTrees into a a format that can be passed to
plotSchedule for schedule availability plots.
"""

# %% Imports
from __future__ import annotations

# Standard Library Imports
from typing import Tuple

# Third Party Imports
from intervaltree import IntervalTree

# %% Function


def intTree2WindowList(schedule_tree: IntervalTree) -> Tuple[list, list, list]:
    """Converts an `IntervalTree`s to an ingestible for `plotSchedule()`.

    Notation:
        M = number of sensors
        N = number of targets
        d = number of availability windows for a given sensor-target pair

    Args:
        schedule_tree (`IntervalTree`): Intervals of sensor-target pair availability.
            The data field in each `Interval` must be a `dict` with the following keys:
                {
                    "target_id": unique_name,
                    "sensor_id": unique_name,
                }

    Returns:
        windows (`list`): [M x N x d] list of lists of lists of pairs
            of tuples, where each nested list is a pair of tuples
            representing the time at the start of an availability window, and
            the duration of that window. d can be any length for each `m` and `n`,
            so long as each entry is a pair of tuples. N must be consistent
            for each M.
        sensor_ids (`list`): List of IDs of sensors that have availability.
        target_ids (`list`): List of IDs of targets that have availability.

    Note that all target and sensor names in `schedule_tree` must be unique.
    """
    # convert IntervalTree to list of Intervals
    list_tree = list(schedule_tree.items())

    # get targets/sensors for each Interval
    target_vec = [interval.data["target_id"] for interval in list_tree]
    sensor_vec = [interval.data["sensor_id"] for interval in list_tree]

    # get unique lists of target/sensor names
    target_ids = list(set(target_vec))
    sensor_ids = list(set(sensor_vec))

    # get number of unique targets/sensors
    num_targets = len(target_ids)
    num_sensors = len(sensor_ids)

    # get start times and durations of each interval
    start_vec = [interval.begin for interval in list_tree]
    dur_vec = [interval.end - interval.begin for interval in list_tree]

    # Assemble inputs for schedule plot
    # initialize availability windows (list of lists)
    windows = [[[] for j in range(num_targets)] for i in range(num_sensors)]

    for i, sens_name in enumerate(sensor_ids):
        # print(f'i={i}, sens_name={sens_name}')
        # get indices of Intervals with with given sensor
        indices = [ctr for ctr, x in enumerate(sensor_vec) if x == sens_name]
        # print(f'indices={indices}')

        # loop through all targets for each sensor
        for j, targ_name in enumerate(target_ids):
            # print(f'j={j}, targ_name={targ_name}')

            # get indices of Intervals with given target
            indices_target = [ctr for ctr, x in enumerate(target_vec) if x == targ_name]

            # get intersection of target-indices and sensor-indices
            intersection = [item for item in indices if item in indices_target]
            # print(f'intersection={intersection}')

            # Next, need to assign intervals that have sense_name in the
            # data field to windows.
            list_of_starts = list(map(start_vec.__getitem__, intersection))
            list_of_durs = list(map(dur_vec.__getitem__, intersection))

            list_of_sets = [[] for x in range(len(list_of_starts))]
            for k, (start, dur) in enumerate(zip(list_of_starts, list_of_durs)):
                list_of_sets[k] = (start, dur)
            windows[i][j] = list_of_sets

    return windows, sensor_ids, target_ids
