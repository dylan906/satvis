"""Visibility history module."""
# %% Imports
from __future__ import annotations

# Third Party Imports
from intervaltree import IntervalTree
from numpy import ndarray, zeros

# satvis Imports
# Sat Vis Imports
from satvis.visibility_func import visibilityFunc, zeroCrossingFit


# %% getVisibility
def getVisHist(
    targets: list[dict],
    sensors: list[dict],
    x_targets: ndarray,
    x_sensors: ndarray,
    time: list,
    planet_radius: float,
) -> tuple[IntervalTree, ndarray]:
    """Generate visibility function history between sensors and targets.

    Args:
        targets (`list[dict]`): N-length list of dicts. Each dict must include
            an 'id' field.
        sensors (`list[dict]`): M-length list of dicts. Each dict must include
            an 'id' field.
        x_targets (`ndarray`): [T x 6 x N] State history of targets. The 1st-
            dimension of the array is the [6x1] ECI state vector [position,
            velocity] in km and km/s, respectively.
        x_sensors (`ndarray`): [T x 6 x M] State history of sensors. The 1st-
            dimension of the array is the [6x1] ECI state vector [position,
            velocity] in km and km/s, respectively.
        time (`list`): [T x 1] list of times corresponding to state histories.
        planet_radius (`float`): assume spherical, km

    Returns:
        rise_set_tree (`IntervalTree`): `IntervalTree` instance of class
            representing all intervals for which target-sensor pairs
            can see each other. If no target-sensor pairs can see each
            other during the input time window, the `IntervalTree` is empty.
            The data field of each entry (`rise_set_tree[#].data`) is a dict
            with the following keys:
                {
                    "target_id": target_id,
                    "sensor_id": sensor_id
                }
        vis (`ndarray`): [M x N x T] array of visibility function values for
            all target-sensor pairs for all time.

    Notation:
        N = Number of targets
        M = Number of sensors
        T = Length of time vector
    """
    num_sensors = len(sensors)
    num_targets = len(targets)

    # preallocate visibility array and list of intervals
    vis = zeros([num_sensors, num_targets, len(time)])
    rise_set_ints = []

    # Calculate visibility function values of all sensor-target pairs
    # loop through sensor-platform pairs
    counter = 0
    for i_sensor in range(num_sensors):
        for i_sat in range(num_targets):
            # sensor-target pair name for labelling interval tree
            pair_name = getPairName(targets[i_sat], sensors[i_sensor])

            # loop through time to calc visibility function
            for i_time in range(len(time)):
                r1 = x_sensors[i_time, :3, i_sensor]
                r2 = x_targets[i_time, :3, i_sat]

                # calc visibility function (ignore supplemental outputs)
                [vis[i_sensor, i_sat, i_time], _, _, _] = visibilityFunc(
                    r1=r1,
                    r2=r2,
                    RE=planet_radius,
                    hg=0,
                )

            _, _, new_tree = zeroCrossingFit(
                vis[i_sensor, i_sat],
                time,
                pair_name,
            )

            # extend list of Intervals (note Intervals are not same as
            # IntervalTree)
            rise_set_ints.extend(list(new_tree))

            counter += 1
    rise_set_tree = IntervalTree(rise_set_ints)
    return rise_set_tree, vis


def getPairName(target: dict, sensor: dict) -> dict:
    """Create a target-sensor pair ID dict.

    Args:
        target (`dict`): Target object
        sensor (`dict`): Sensor object

    Returns:
        pair_name (`dict`): {'target_id': target_id, 'sensor_id': sensor_id}
    """
    target_id = target["id"]
    sensor_id = sensor["id"]

    pair_name = {"target_id": target_id, "sensor_id": sensor_id}
    return pair_name
