# **sat-vis**: A satellite visibility calculator.
## Description
*sat-vis* is a small library of functions used to calculate line-of-sight (LOS) visibility between spacecraft and plot access windows. The core functions that the library is based on are implementations of algorithms developed by J. A. Lawton and Salvatore Alfano et. al. Visibility windows are represented as `IntervalTree`s. Access windows are plotted using matplotlib.

## Install
```
pip install sat-vis
```

## Examples
### Example 1

To calculate the visibility between two Earth-centered-inertial (ECI) points:
```python
earth_radius = 6378 # km
extra_height = 0 # km
r1 = array([[earth_radius + 400, 0, 0]]).transpose() # position of object 1
r2 = array([[earth_radius, 0, 0]]).transpose() # position of object 2

[vis, phi, a1, a2] = visibilityFunc(r1, r2, earth_radius, extra_height)
print(vis)
print(phi)
print(a1)
print(a2)

# Prints:
# 0.3451182504723773
# 0.00014753614577624565
# 0.34526578661815355
# 0.0
```
where `vis` is the value of the visibility function, `phi` is the angle (in radians) drawn between the two Earth-centered-inertial points, and `a1` and `a2` are intermediate construction angles. A value of `vis`>0 means that the two points have a direct LOS to each other.

### Example 2
If you just want to know if two points are visible to each other in a binary fashion, use `isVis`:
```python
[vis_bool] = isVis(r1, r2, earth_radius, extra_height)
print(vis_bool)
# True
```

### Example 3
A series of visibility function values can be represented as a couple of `ndarray`s or an `IntervalTree` via the `zeroCrossingFit` function. This is handy if you want to calculate visibility windows between two objects.
```python
t = array([0, 1, 2, 3, 4]) # time vector
vis = array([-1, -0.1, 0.5, 4, 2]) # objects become visible to each other between t[1] and t[2]
[crossings, rise_set, vis_tree] = zeroCrossingFit(vis, t)
print(crossings)
print(rise_set)
print(vis_tree)

# Prints:
# [1.40896106] 
# [1.]
# tree=IntervalTree([Interval(1.4089610649024726, 4)])
```
Where `crossings` is a list of times at which the visibility function value crosses zero, `rise_set` indicates the direction of the crossing (1=rise, -1=set), and `tree` is an `IntervalTree` indicating time windows during which the visibility function value is positive. See the [IntervalTree package](https://github.com/chaimleib/intervaltree) on GitHub for details on its structure.

### Example 4
If the two objects never see each other, the returned arrays and `IntervalTree` are empty.
```python
vis = array([-1, -0.1, -0.5, -4, -2]) 
[crossings, rise_set, vis_tree] = zeroCrossingFit(vis, t)
print(crossings)
print(rise_set)
print(vis_tree)
# []
# []
# IntervalTree()
```

### Example 5
You can assign an identifier to `Interval`s within an `IntervalTree`. This is useful if you combine multiple `IntervalTree`s representing more than two objects.
```python
vis1 = array([-1, -0.1, 0.5, 4, 2])
vis2 = array([-2, -1, -0.5, 1, 1.1]) 
[_, _, vis_tree1] = zeroCrossingFit(vis1, t, "pair1")
[_, _, vis_tree2] = zeroCrossingFit(vis2, t, "pair2")
combined_tree = vis_tree1 | vis_tree2
print(vis_tree1)
print(vis_tree2)
print(combined_tree)
# tree=IntervalTree([Interval(1.4089610649024726, 4, 'pair1)])
# tree=IntervalTree([Interval(2.328702338492417, 4, 'pair2')])
# IntervalTree([Interval(1.4089610649024726, 4, 'pair1'), Interval(2.328702338492417, 4, 'pair2')])

```
## Citations:
- Alfano, Salvatore & Jr, Negron, & Moore, Jennifer. (1992). Rapid Determination of Satellite Visibility Periods. Journal of The Astronautical Sciences. Vol. 40, April-June, pp 281-296. 
- Lawton, J. A.. (1987). Numerical Method for Rapidly Determining Satellite-Satellite and Satellite-Ground Station In-View Periods. Journal of Guidance, Navigation and Control. Vol. 10, January-February, pp. 32-36
- Chaim Leib Halbert's IntervalTree package on GitHub, https://pypi.org/project/intervaltree/#description

