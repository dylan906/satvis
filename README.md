# **SatVis**: A satellite visibility calculator.
## Description
SatVis is a small library of functions used to calculate line-of-sight (LOS) visibility between spacecraft assuming a spherical Earth. The functions within the library are implementations of algorithms developed by J. A. Lawton and Salvatore Alfano et. al.

## Examples
### Example 1

Entering this:
```python
earth_radius = 6378 # km
extra_height = 0 # km
r1 = array([[RE + 400, 1, 0]]).transpose() # position of object 1
r2 = array([[RE, 0, 0]]).transpose() # position of object 2

[vis, phi, a1, a2] = visibilityFunc(r1, r2, earth_radius, extra_height)
```
returns this:
```python
vis = 0.3451182504723773
phi = 0.00014753614577624565
a1 = 0.34526578661815355
a2 = 0.0
```
where `vis` is the value of the visibility function, `phi` is the angle (in radians) drawn between the two Earth-centered-inertial points, and `a1` and `a2` are intermediate construction angles. A value of `vis`>0 means that the two points have a direct LOS to each other.

### Example 2
If you just want to know if two points are visible to each other in a binary fashion, use `isVis`:
```python
[vis_bool] = isVis(r1, r2, earth_radius, extra_height)
> True
```

## Citations:
- Alfano, Salvatore & Jr, Negron, & Moore, Jennifer. (1992). Rapid Determination of Satellite Visibility Periods. Journal of The Astronautical Sciences. Vol. 40, April-June, pp 281-296. 
- Lawton, J. A.. (1987). Numerical Method for Rapidly Determining Satellite-Satellite and Satellite-Ground Station In-View Periods. Journal of Guidance, Navigation and Control. Vol. 10, January-February, pp. 32-36

