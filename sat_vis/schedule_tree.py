"""Schedule tree: module for defining ScheduleTree class and creating
    instances."""
# %% Imports
from __future__ import annotations

# Third Party Imports
from intervaltree import IntervalTree
from numpy import append, ndarray, zeros

# Punch Clock Imports
from scheduler_testbed.common.constants import getConstants
from scheduler_testbed.common.utilities import checkPlatform, getInitialConditions
from scheduler_testbed.dynamics.dynamics import satelliteDynamics, terrestrialDynamics
from scheduler_testbed.dynamics.propagator import simplePropagate
from scheduler_testbed.schedule_tree.visibility_func import visibilityFunc, zeroCrossingFit


# %% Class Definition
class ScheduleTree:
    """ScheduleTree contains an IntervalTree of visibility windows between
    sensor-target pairs (self.sched_tree). Also contains some handy
    properties of the instance and useful functions for easily getting
    information from self.sched_tree.
    """

    def __init__(self, interval_tree: IntervalTree):
        """Initialize ScheduleTree() instance.

        Args:
            interval_tree (``IntervalTree``): An instance of an IntervalTree
                with dicts in the data fields of every Interval instance
                with the following format:

                    {"targ_id": target_name,
                    "sensor_id": sensor_name}

            All Intervals in the IntervalTree must have dicts with the
            target-sensor-pair names.
        """

        self.sched_tree = interval_tree

        targ_list = []
        sens_list = []

        for i in range(len(self.sched_tree)):
            targ_id = self.getTargAtInt(i)
            sens_id = self.getSensAtInt(i)

            targ_list.append(targ_id)
            sens_list.append(sens_id)

        # get unique IDs and order
        self.targ_list = sorted(set(targ_list))
        self.sens_list = sorted(set(sens_list))

        self.num_targs = len(self.targ_list)
        self.num_sens = len(self.sens_list)

    def getTargAtInt(self, interval_num):
        tree_list = list(self.sched_tree)
        targ_id = tree_list[interval_num][2]["targ_id"]
        return targ_id

    def getSensAtInt(self, interval_num):
        sens_id = list(self.sched_tree)[interval_num][2]["sensor_id"]
        return sens_id

    def getStartAtInt(self, interval_num):
        start_time = list(self.sched_tree)[interval_num][0]
        return start_time

    def getFinishAtInt(self, interval_num):
        finish_time = list(self.sched_tree)[interval_num][1]
        return finish_time

    def getTargs(self, time):
        list_tree = list(self.sched_tree[time])
        targets = [x[2]["targ_id"] for x in list_tree]
        return sorted(set(targets))

    def getSens(self, time):
        list_tree = list(self.sched_tree[time])
        sensors = [x[2]["sensor_id"] for x in list_tree]
        return sorted(set(sensors))

    def isVis(self, time, sens_id, targ_id):
        list_tree = list(self.sched_tree[time])
        if len(list_tree) == 0:
            return False

        for i, window in enumerate(list_tree):
            if (window[2]["sensor_id"] == sens_id) and (window[2]["targ_id"] == targ_id):
                return True
            else:
                vis_status = False

        return vis_status


# %% Rise-Set Function
def getRiseSet(
    targets: list[dict],
    sensors: list[dict],
    t: list,
) -> tuple:
    """Generates target-sensor pair access windows.

    Args:
        targets (`list[dict]`): List of dictionaries of target agents
            according to standard format.
        sensors (`list[dict]`): List of dictionaries of sensor agents
            according to standard format.
        t (`list`): List of times (s) at which motion propagation will be
            evaluated. No need to use fine resolution, just fine enough so
            that a pass between two objects won't be skipped over.

    Returns:
        rise_set_tree (`ScheduleTree`): Instance of custom class
            ScheduleTree.
        v (`ndarray`): [N X M X T] array where T is the number of elements
            in t, N is the number of sensors, and M is the number of
            satellites. Values of v are the values of the visibility function
            evaluated at input t. Positive values mean the target-sensor
            pair can see each other.
        x_sensors (`ndarray`): [6 x T x N] State history of sensors.
        x_targs (`ndarray`): [6 x T x M] State history of targets.
    """
    x0 = getInitialConditions(targets)
    agent_types = checkPlatform(targets)
    x0 = append(x0, getInitialConditions(sensors), axis=1)
    agent_types = agent_types + checkPlatform(sensors)

    # create list of dynamics types
    dynamics_list = []
    for agent in agent_types:
        if agent == "ground":
            dynamics_list.append(None)
        elif agent == "sat":
            dynamics_list.append(satelliteDynamics)
        else:
            print("Error: Unexpected agent type")

    # initialize state history
    x_hist = zeros([6, len(t), x0.shape[1]])

    # set initial values of x_hist
    x_hist[:, 0, :] = x0

    # loop through agents
    for i, (x_init, dynamics) in enumerate(zip(x0.transpose(), agent_types)):
        # loop through time and propagate state history
        for j, tf in enumerate(t[1:], start=1):
            if dynamics == "sat":
                x_now = simplePropagate(
                    satelliteDynamics,
                    x_init,
                    t0=t[j - 1],
                    tf=tf,
                ).squeeze()
                x_hist[:, j, i] = x_now
                x_init = x_now
            elif dynamics == "ground":
                x_now = terrestrialDynamics(
                    t=tf,
                    x0=x_init,
                    JD=t[j - 1],
                ).squeeze()
                x_hist[:, j, i] = x_now
                x_init = x_now

    x_targs = x_hist[:, :, : len(targets)]
    x_sensors = x_hist[:, :, len(targets) :]
    # caluclate visibility over state history
    rise_set_tree, v = getVisHist(targets, sensors, x_targs, x_sensors, t)

    return ScheduleTree(rise_set_tree), v, x_sensors, x_targs


# %% getVisibility
def getVisHist(
    targets: list[dict],
    sensors: list[dict],
    x_targs: ndarray,
    x_sensors: ndarray,
    t: ndarray,
):
    """Generates visibility function history between N sensors and M satellites.

    Args:
        targets (``list[dict]``): N-length list of dicts. Each dict must include a
            'sat_num' field.
        sensors (_type_): M-length list of dicts. Each dict must include an
            'id' field.
        x_targs (``ndarray``): [6 x T x N] State history of targets,
            where T is the number of time steps, N is the number of target,
            and the 1st-dimension of the array is the [6x1] ECI state vector
            [position, velocity].
        x_sensors (``ndarray``): [6 x T x M] State history of sensors, where T
            is the number of time steps, M is the number of sensors, and
            the 1st-dimension of the array is the [6x1] ECI state vector
            [position, velocity].
        t (``ndarray``): [T x 1] array (or list) of times corresponding to
            state histories.

    Returns:
        rise_set_tree (``IntervalTree``): IntervalTree instance of class
            representing all intervals for which target-sensor pairs
            can see each other. If no target-sensor pairs can see each
            other during the input time window, the IntervalTree will be
            empty.
        v (``ndarray``): [N x M x T] array of visibility function values for
            all target-sensor pairs for all time.
    """
    RE = getConstants()["earth_radius"]

    num_sensors = len(sensors)
    num_targs = len(targets)

    # preallocate visibility array and list of intervals
    v = zeros([num_sensors, num_targs, len(t)])
    rise_set_ints = []

    # Calculate visibility function values of all sensor-target pairs
    # loop through sensor-platform pairs
    counter = 0
    for i_sensor in range(num_sensors):
        # # check altitude (of ground sensors only) for h restriction.
        # h = getAltBound(sensors[i_sensor])
        # Potentially assign Earth radius here for visibilityFunc.

        for i_sat in range(num_targs):
            # sensor-target pair name for labelling interval tree
            pair_name = getPairName(targets[i_sat], sensors[i_sensor])

            # loop through time to calc visibility function
            for i_time in range(len(t)):
                r1 = x_sensors[:3, i_time, i_sensor]
                r2 = x_targs[:3, i_time, i_sat]

                # calc visibility function (ignore supplemental outputs)
                [v[i_sensor, i_sat, i_time], _, _, _] = visibilityFunc(
                    r1=r1,
                    r2=r2,
                    RE=RE,
                    hg=0,
                )

            _, _, new_tree = zeroCrossingFit(v[i_sensor, i_sat], t, pair_name)

            # extend list of Intervals (note Intervals are not same as
            # IntervalTree)
            rise_set_ints.extend(list(new_tree))

            counter += 1
    rise_set_tree = IntervalTree(rise_set_ints)
    return rise_set_tree, v


def getPairName(target: dict, sensor: dict):
    """Creates a target-sensor pair ID dict.

    Args:
        target (``dict``): Satellite object
        sensor (``dict``): Satellite or terrestrial object

    Returns:
        pair_name (``dict``): {'targ_id': sat_id, 'sensor_id': sensor_id}
    """
    sat_id = target["sat_num"]

    # check for space-based sensor
    if checkPlatform(sensor) == ["ground"]:
        sensor_id = sensor["id"]
    else:
        sensor_id = sensor["sat_num"]

    # pair_name = str(sat_id) + '-' + str(sensor_id)
    pair_name = {"targ_id": sat_id, "sensor_id": sensor_id}
    return pair_name
