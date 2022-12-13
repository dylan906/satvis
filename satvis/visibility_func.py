"""Functions that calculate LOS visibility between two points near a spherical body."""
# %% Imports
from __future__ import annotations

# Standard Library Imports
from typing import Tuple
from warnings import warn

# Third Party Imports
from intervaltree import Interval, IntervalTree
from numpy import append, arange, arccos, array, dot, isnan, isreal, ndarray, sign
from numpy.linalg import norm
from numpy.polynomial import Polynomial


# %% Visibility function
def visibilityFunc(
    r1: ndarray,
    r2: ndarray,
    RE: float,
    hg: float,
) -> Tuple[float, float, float, float]:
    """Calculate visibility function for two position vectors.

    Args:
        r1 (`ndarray`): [3 X 1] ECI position vector of object 1
        r2 (`ndarray`): [3 X 1] ECI position vector of object 2
        RE (`float`): Radius of planet
        hg (`float`): extra height restriction above planet surface

    Returns:
        v (`float`): value of visibility function (positive indicates objects
            can see each other)
        phi (`float`): angle between position vectors
        alpha1 (`float`): construction angle 1
        alpha2 (`float`): construction angle 2

    From "Numerical Method for Rapidly Determining Satellite-Satellite
        and Satellite-Ground Station In-View Periods", by Lawton, 1987.
        All argument units are arbitrary distances, just keep consistent.
    """
    # small value for error threshold
    eps = 1e-13

    RE_prime = RE + hg
    r1_mag = norm(r1)
    r2_mag = norm(r2)

    # check if points are far below surface of Earth
    if RE_prime / r1_mag > (1 + eps):
        print(
            f"RE_prime/r1_mag={RE_prime/r1_mag}, (RE_prime={RE_prime}, r1_mag={r1_mag})"
        )
        # raise ValueError("RE_prime > r1_mag")
        warn("RE_prime > r1_mag")

    if RE_prime / r2_mag > (1 + eps):
        print(
            f"RE_prime/r2_mag={RE_prime/r2_mag}, (RE_prime={RE_prime}, r2_mag={r2_mag})"
        )
        # raise ValueError("RE_prime > r2_mag")
        warn("RE_prime > r2_mag")

    # if points are slightly below Earth surface, change to be on surface.
    if (RE_prime / r1_mag > 1) and (RE_prime / r1_mag < 1 + eps):
        r1_mag = RE_prime

    if (RE_prime / r2_mag > 1) and (RE_prime / r2_mag < 1 + eps):
        r2_mag = RE_prime

    alpha1 = arccos(RE_prime / r1_mag)
    alpha2 = arccos(RE_prime / r2_mag)

    # check if numerics cause test_var to be >1, and correct if needed
    # Corrects for issues when vectors are close to each other
    test_var = dot(r1.squeeze(), r2.squeeze()) / (r1_mag * r2_mag)
    if test_var > (1 + eps):
        print(f"dot(r1, r2)/(r1_mag * r2_mag)={dot(r1, r2)/(r1_mag * r2_mag)}")
        raise ValueError("dot(r1, r2)/(r1_mag * r2_mag) > 1")
    elif test_var < (-1 - eps):
        print(f"dot(r1, r2)/(r1_mag * r2_mag)={dot(r1, r2)/(r1_mag * r2_mag)}")
        raise ValueError("dot(r1, r2)/(r1_mag * r2_mag) < -1")
    elif test_var > 1 and test_var < (1 + eps):
        test_var = 1
    elif test_var < -1 and test_var > (-1 - eps):
        test_var = -1

    phi = arccos(test_var)
    # print(np.dot(r1, r2)/(r1_mag * r2_mag))

    # Correct alphas if they are outside doman of arccos
    if isnan(alpha1):
        alpha1 = 0
        warn("alpha1 changed from NaN to 0")
    if isnan(alpha2):
        alpha2 = 0
        warn("alpha2 changed from NaN to 0")

    v = alpha1 + alpha2 - phi

    # the checks for r_mag and test_var should ensure that v is a real number,
    # but just in case, check again
    if isnan(v):
        print(f"alpha1={alpha1}, alpha2={alpha2}, phi={phi}")
        print(f"r1={r1}, r2={r2}")
        print(f"r1_mag={r1_mag}, r2_mag={r2_mag}")
        raise TypeError("Error: v is NaN")

    return v, phi, alpha1, alpha2


# %% Calculate visibility windows
def zeroCrossingFit(
    v: ndarray,
    t: ndarray,
    id: object = None,
) -> Tuple[ndarray[float], ndarray[float], IntervalTree]:
    """Interpolates visibility windows from sparse visibility data.

        Fit curves around zero-crossings of visibility function.
        Fit cubic polynomials to every 4 points, so loop through t[3] - t[end].
        Outputs interval tree object of visibility windows.

        Based on: Alfano, Salvatore, Negron, David Jr., Moore, Jennifer L.,
        “Rapid Determination of Satellite Visibility Periods,” Journal of
        Astronautical Sciences, Vol. 40, No. 2, 1992
    Args:
        v (`ndarray`): [1 x N] array of floats
        t (`ndarray`): [1 x N] array of floats
        id (`any`): (Optional) Identifier for interval tree

    Returns:
        crossings (`ndarray`): [1 x M] array of times at which the
            visibility function crosses 0
        riseSet (`ndarray`): [1 x M] array of +-1 indicating if associated
            value in crossings is a rise point (+1) or set point (-1)
        tree (`IntervalTree`): Interval tree object of time bounds during
            which visibility function is >1

    Note that the ability to detect rise/set times within the first 2 steps
        of the beginning or end of `t` is sketchy due to the 4-point curve
        fit requirement. Workaround is in-place that does a 1st-order polyfit
        when t[0] and t[1] straddle v=0.
    """
    # initialize
    crossings = []
    riseSet = []
    tree = IntervalTree()
    crossIndx = -1

    # Special case: no-zero crossings, V is positive for all time
    if all(sign(v) == 1):
        temp = Interval(t[0], t[-1], id)
        tree.add(temp)
        # print('special case: visible for whole time vector')
        return crossings, riseSet, tree
    # special case: no-zero crossings, V is negative for all time
    elif all(sign(v) == -1):
        # Note: IntervalTree object does not allow null (empty) intervals
        # print('special case: no visibility windows')
        return crossings, riseSet, tree

    # special case: zero-crossing occurs between t[0] and t[1]
    # 1st-order polyfit exception.
    if sign(v[0]) != sign(v[1]):
        crossings = append(crossings, findCrossing(t[:2], v[:2], 1))
        crossIndx += 1
        riseSet = append(riseSet, riseOrSet(v[1]))
        if riseSet[0] == -1:
            temp = Interval(t[0], crossings[0], id)
            tree.add(temp)

    # iterate through time vector for all other cases
    for i in arange(3, len(t)):
        # print('i =' + str(i))
        if i == 3:
            #  starting visibility sign (+1 or -1)
            startV = sign(v[0])

        # fit with 2 mid-points on either side of zero
        if sign(v[i - 1]) != sign(v[i - 2]):
            crossIndx += 1

            # print('i =' + str(i))
            # grab 4 time values
            tSnapshot = array([t[i - 3], t[i - 2], t[i - 1], t[i]])
            # grab 4 v values
            vSnapshot = array([v[i - 3], v[i - 2], v[i - 1], v[i]])

            crossings = append(crossings, findCrossing(tSnapshot, vSnapshot, 3))

            # determine if zero-crossing was a rise or set time and assign
            # val to vector
            riseSet = append(riseSet, riseOrSet(v[i - 1]))

            # Construct interval tree for times when v > 0 (visibility
            # windows)
            # wait for 2 crossings to appear, where 2nd crossing is a
            # set time
            if len(crossings) > 1 and sign(riseSet[crossIndx]) == -1:
                temp = Interval(crossings[crossIndx - 1], crossings[crossIndx], id)
                tree.add(temp)
            # create interval if satellite starts in visibility window
            elif len(crossings) == 1 and startV == 1:
                temp = Interval(t[0], crossings[crossIndx], id)
                tree.add(temp)
                # print('special case: first visibility window start
                #        at t0')

        # create interval if simulation ends while visible
        if i == len(t) - 1:
            # at least one crossing has occurred
            if crossIndx >= 0 and sign(v[i]) == 1:
                temp = Interval(crossings[crossIndx], t[i], id)
                tree.add(temp)

    return crossings, riseSet, tree


def findCrossing(
    t: ndarray,
    v: ndarray,
    order: int,
) -> ndarray[float]:
    """Fits a 3rd order polynomial to 4 points and finds root.

    Args:
        t (`ndarray`): [4,] Time values.
        v (`ndarray`): [4,] Visibility function values.
        order (`int`): Order of polyfit.

    Returns:
        `ndarray[float]`: [1, ] Time of zero-crossing.
    """
    # fit a 3rd-order polynomial
    poly = Polynomial.fit(t, v, order)
    # find roots of polynomial
    polyRoots = poly.roots()
    # discard complex roots
    realRoots = polyRoots[isreal(polyRoots)].real

    # get roots that are in domain (range) of the
    # polynomial (t[i-3] and t[i])
    # values of t where 0-crossings occurred
    inRangeRoots = realRoots[(realRoots < poly.domain[1]) & (realRoots > poly.domain[0])]

    return inRangeRoots


def riseOrSet(v_i: float) -> int:
    """Switch case for visibility value.

    Args:
        v_i (`float`): Value of visibility function

    Returns:
        `int`: 1, -1, or 0 for rise, set, or anomaly, respectively.
    """
    if sign(v_i) == 1:
        # rise time
        riseSet = 1
    elif sign(v_i) == -1:
        # set time
        riseSet = -1
    else:
        riseSet = 0  # anomaly-->bad!

    return riseSet


def isVis(
    r1: ndarray,
    r2: ndarray,
    RE: float,
    hg: float = 0,
) -> bool:
    """Shortcut wrapper to for boolean visibility.

    Args:
        r1 (`ndarray`): [3 X 1] ECI position vector of object 1
        r2 (`ndarray`): [3 X 1] ECI position vector of object 2
        RE (`float`): Radius of planet
        hg (`float`): extra height restriction above planet surface

    Returns:
        `bool`: True if `r1` and `r2` are visible to each other.
    """
    v, _, _, _ = visibilityFunc(r1, r2, RE, hg)

    # convert to regular bool from numpy.bool
    return bool(v > 0)
