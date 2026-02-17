# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/4-vehicle-state-management

Vehicle State Management is the central system for representing and tracking all static and dynamic state information about vehicles in WayWise. This includes position tracking across multiple coordinate frames and sensor sources, vehicle geometry and kinematics, steering and motion calculations, and support for articulated vehicles (truck-trailer combinations).

This page covers the `VehicleState`

hierarchy and its specializations (`CarState`

, `TruckState`

, `TrailerState`

), position tracking via `PosPoint`

structures, and the integration with autopilot systems. For information about how autopilot algorithms consume vehicle state, see Pure Pursuit Waypoint Follower. For coordinate transformation utilities, see Coordinate Systems & Transformations.

The vehicle state system is built on a class hierarchy that separates generic object state from vehicle-specific state:

**Sources:** vehicles/objectstate.h1-91 vehicles/vehiclestate.h1-151 vehicles/carstate.h1-69 vehicles/truckstate.h1-60 vehicles/trailerstate.h1-55

VehicleState maintains separate position estimates from different sources, indexed by `PosType`

:

| PosType | Description | Usage |
|---|---|---|
`simulated` | Simulated/default position | Base state, legacy compatibility |
`fused` | Sensor-fused position estimate | Primary position for autopilot |
`odom` | Odometry-based position | Dead reckoning from wheel encoders |
`IMU` | IMU-derived position | Inertial navigation |
`GNSS` | Raw GNSS position | GPS/RTK positioning |
`UWB` | Ultra-wideband positioning | Indoor/local positioning |

**Sources:** vehicles/vehiclestate.h134 vehicles/vehiclestate.cpp13-24 core/pospoint.h (referenced), autopilot/purepursuitwaypointfollower.cpp23-29

VehicleState defines several reference points relative to the rear axle, which is the primary reference point for all vehicles:

**Offset Management:**

| Offset | Type | Purpose | Set By |
|---|---|---|---|
`mRearAxleToCenterOffset` | `xyz_t` | Vehicle geometric center | `setLength()` |
`mRearAxleToRearEndOffset` | `xyz_t` | Back bumper position | `setLength()` (0.1-0.25 × length) |
`mRearAxleToHitchOffset` | `xyz_t` | Trailer hitch point | `setLength()` for truck |

**Sources:** vehicles/vehiclestate.h64-72 vehicles/carstate.cpp18-23 vehicles/truckstate.cpp20-24 vehicles/trailerstate.cpp21-27

The method `posInVehicleFrameToPosPointENU()`

transforms a point from the vehicle's local coordinate frame to the global ENU (East-North-Up) frame:

**Usage Example (from autopilot):**

**Sources:** vehicles/vehiclestate.h77-78 vehicles/vehiclestate.cpp92-97

`CarState`

implements a bicycle kinematic model for vehicles with Ackermann steering geometry:

**Key Parameters:**

| Parameter | Type | Default/Calculation | Description |
|---|---|---|---|
`mAxisDistance` | `double` | `0.6 × length` if unset | Wheelbase distance [m] |
`mMaxSteeringAngle` | `double` | `π/4` (45°) if unset | Maximum steering angle [rad] |
`mMinTurnRadiusRear` | `double` | ∞ initially | Minimum turn radius constraint [m] |

**Sources:** vehicles/carstate.h38-55 vehicles/carstate.cpp13-23

The `updateOdomPositionAndYaw()`

method implements dead reckoning using the bicycle model:

**Sources:** vehicles/carstate.cpp268-303

Two key methods convert between control representations:

**1. getCurvatureToPointInVehicleFrame(point) - Pure Pursuit Steering:**

```
Input: QPointF point (x, y) in vehicle frame
Output: curvature κ [1/m]
κ = -2y / (x² + y²)
```


This implements the pure pursuit algorithm's core calculation. The curvature represents the instantaneous rate of change of heading.

**2. steeringCurvatureToSteering(steeringCurvature) - Convert to Steering Command:**

```
Input: curvature κ [1/m]
Output: normalized steering [-1.0, 1.0]
δ = atan(L × κ) // Convert to angle
δ = clamp(δ, -max_angle, max_angle) // Apply limits
steering = δ / max_angle // Normalize
```


**Sources:** vehicles/vehiclestate.cpp119-133 vehicles/carstate.cpp305-312

`TruckState`

extends `CarState`

to support truck-trailer combinations, with the trailer angle as a key state variable:

**Trailer Angle Convention:**

**Sources:** vehicles/truckstate.h33-35 vehicles/truckstate.cpp122-124

The `updateTrailingVehicleOdomPositionAndYaw()`

method maintains trailer state during motion:

**Key Equations:**

For **simulated trailer angle** (odometry mode):

```
φ_{n+1} = φ_n + (Δd / L_trailer) × sin(θ_truck - θ_trailer)
```


For **trailer position** from hitch:

```
P_trailer = P_hitch + R(θ_trailer) × offset_hitch_to_axle
```


**Sources:** vehicles/truckstate.cpp58-82

The `getCurvatureWithTrailer()`

method calculates steering curvature accounting for trailer dynamics:

**Forward Motion (speed > 0):**

```
θ_err = atan2(y_target, x_target)
φ_desired = atan(2 × L_trailer × sin(θ_err))
κ = gain_forward × (φ_actual - φ_desired) - sin(φ_actual) / L_trailer
κ_final = κ / cos(φ_actual)
```


**Reverse Motion (speed < 0):**

```
x_trailer = -L_trailer × cos(-φ)
y_trailer = -L_trailer × sin(-φ)
θ_err = atan2(y_target - y_trailer, x_target - x_trailer) - (-φ)
φ_desired = atan(2 × L_trailer × sin(θ_err) / lookahead_radius)
κ = gain_reverse × (φ_actual - φ_desired) - sin(φ_actual) / L_trailer
κ_final = κ / cos(φ_actual)
```


**Gains:**

`mPurePursuitForwardGain`

: Default = 1.0`mPurePursuitReverseGain`

: Default = -1.0**Sources:** vehicles/truckstate.cpp84-107 vehicles/truckstate.h24-28

The autopilot system needs to determine which part of the vehicle (truck or trailer) should be used as the reference point for navigation, especially during backing maneuvers:

**Usage in Autopilot:**

**Position Reference** (autopilot/purepursuitwaypointfollower.cpp54-58):

**End Goal Alignment** (autopilot/purepursuitwaypointfollower.cpp503-527):

`REAR_AXLE`

, `CENTER`

, or `FRONT_REAR_END`

alignment types**Curvature Calculation** (vehicles/truckstate.cpp26-32):

**Sources:** autopilot/purepursuitwaypointfollower.cpp530-540 vehicles/truckstate.cpp26-32

VehicleState supports different alignment strategies for end goal precision:

**Implementation:**

The alignment type is stored in `VehicleState::mEndGoalAlignmentType`

and used by autopilot to determine when a waypoint is reached:

| Type | Reference Point | Use Case |
|---|---|---|
`REAR_AXLE` | Rear axle (0,0,0) | General navigation, default |
`CENTER` | Geometric center | Precision parking, centering |
`FRONT_REAR_END` | Front end (forward) or rear end (backing) | Loading docks, precise positioning |

**Sources:** vehicles/vehiclestate.h23-95 autopilot/purepursuitwaypointfollower.cpp503-527 vehicles/carstate.cpp331-334

VehicleState manages the ENU (East-North-Up) coordinate system reference point for coordinate transformations:

**Default Reference Locations:**

`{57.71495867, 12.89134921, 0}`

(used in code)`{57.7810, 12.7692, 0}`

`{57.6876, 11.9807, 0}`

**Sources:** vehicles/vehiclestate.h60-129 vehicles/vehiclestate.cpp150-160 autopilot/purepursuitwaypointfollower.cpp640-665

VehicleState classes provide their configurable parameters to the `ParameterServer`

for runtime adjustment:

**Sources:** vehicles/carstate.cpp314-335 vehicles/truckstate.cpp126-139 vehicles/trailerstate.cpp29-52

**Sources:** autopilot/purepursuitwaypointfollower.cpp50-59 autopilot/purepursuitwaypointfollower.cpp380-411 vehicles/vehiclestate.cpp129-133

The autopilot can be configured to use different position sources via `setPosTypeUsed()`

:

**Sources:** autopilot/purepursuitwaypointfollower.h110 autopilot/purepursuitwaypointfollower.cpp418-421

| Method | Class | Purpose | Returns |
|---|---|---|---|
`getPosition(PosType)` | VehicleState | Get position from specific source | PosPoint |
`setPosition(PosPoint&)` | VehicleState | Update position for source type | void |
`posInVehicleFrameToPosPointENU(xyz_t, PosType)` | VehicleState | Transform vehicle frame to ENU | PosPoint |
`getCurvatureToPointInVehicleFrame(QPointF)` | VehicleState | Calculate pure pursuit curvature | double [1/m] |
`getCurvatureToPointInENU(QPointF, PosType)` | VehicleState | Calculate curvature from ENU point | double [1/m] |
`updateOdomPositionAndYaw(double, PosType)` | CarState | Update position via odometry | void |
`steeringCurvatureToSteering(double)` | CarState | Convert curvature to steering command | double [-1,1] |
`getTurnRadiusRear()` | CarState | Get current turn radius | double [m] |
`getBrakingDistance()` | CarState | Calculate stopping distance | double [m] |
`getCurvatureWithTrailer(QPointF)` | TruckState | Trailer-aware curvature calculation | double [1/m] |
`updateTrailingVehicleOdomPositionAndYaw(double, PosType)` | TruckState | Update trailer position/angle | void |
`getTrailerAngleRadians()` | TruckState | Get articulation angle | double [rad] |
`getReferenceVehicleState()` | PurepursuitWaypointFollower | Select truck or trailer reference | QSharedPointer |

**Sources:** vehicles/vehiclestate.h vehicles/carstate.h vehicles/truckstate.h autopilot/purepursuitwaypointfollower.h

Refresh this wiki
