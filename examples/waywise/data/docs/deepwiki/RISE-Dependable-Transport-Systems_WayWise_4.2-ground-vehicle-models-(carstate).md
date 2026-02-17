# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/4.2-ground-vehicle-models-(carstate)

This document describes the ground vehicle models implemented in WayWise, covering Ackermann steering kinematics with trailer support. The implementation consists of three primary classes:

`CarState`

`TruckState`

`CarState`

with trailer articulation support`TrailerState`

These classes provide kinematics for odometry updates, steering curvature calculations, and complex trailer backing maneuvers used by the Pure Pursuit autopilot.

For information about the base `VehicleState`

architecture and position management, see Vehicle State Architecture. For multicopter models, see Multicopter Model.

**Sources:** vehicles/carstate.h1-69 vehicles/truckstate.h1-60 vehicles/trailerstate.h1-55

The ground vehicle models extend the `VehicleState`

base class with specialized implementations for Ackermann steering vehicles:

**Sources:** vehicles/objectstate.h22-29 vehicles/carstate.h20 vehicles/truckstate.h13 vehicles/trailerstate.h19

`CarState`

implements a basic Ackermann steering vehicle with bicycle kinematic model for odometry updates.

| Property | Type | Description | Default |
|---|---|---|---|
`mAxisDistance` | `double` | Wheelbase between front and rear axles [m] | 0.6 × length if unset |
`mMaxSteeringAngle` | `double` | Maximum steering angle [rad] | π/4 (45°) if unset |
`mMinTurnRadiusRear` | `double` | Minimum turn radius at rear axle [m] | Calculated from max steering |

**Sources:** vehicles/carstate.h38-61

The steering model uses a simplified representation where `steering ∈ [-1.0, 1.0]`

approximates `tan(steering_angle)`

. This allows direct calculation of turn radii without expensive trigonometric operations in the control loop.

**Steering Calculation Pipeline**

**Implementation Methods:**

| Method | Location | Description |
|---|---|---|
`steeringCurvatureToSteering(double)` | vehicles/carstate.cpp305-312 | Converts curvature to steering value: `atan(L × κ) / θ_max` |
`getTurnRadiusRear()` | vehicles/carstate.h47 | Returns `mAxisDistance / -steering` |
`getTurnRadiusFront()` | vehicles/carstate.h48 | Returns `√(mAxisDistance² + R_rear²)` |
`setSteering(double)` | vehicles/carstate.cpp225-230 | Clamps steering to `±tan(mMaxSteeringAngle)` |

**Sources:** vehicles/carstate.cpp225-230 vehicles/carstate.cpp305-312 vehicles/carstate.h47-48

The `updateOdomPositionAndYaw()`

method vehicles/carstate.cpp268-303 implements a bicycle kinematic model with the rear axle as the reference point. This is the fundamental method for dead-reckoning position updates when odometry sensors are used.

**Bicycle Model Odometry Flow**

**Turning Motion Details:**

The circular arc motion uses the average of front and rear turn radii:

```
R_avg = (getTurnRadiusRear() + getTurnRadiusFront()) / 2
Δyaw = drivenDistance / R_avg
```


Position update accounts for circular arc geometry, with the rear axle following the arc of radius `R_rear`

.

**Sources:** vehicles/carstate.cpp268-303 vehicles/carstate.h47-48

`CarState`

provides methods for calculating safe stopping distances used by the emergency brake system and collision avoidance:

**Braking Methods**

| Method | Return Type | Formula | Purpose |
|---|---|---|---|
`getBrakingDistance()` | `double` | `d = v × t_r - 0.5(v + a×t_r)² / a_brake` | Distance to stop at max deceleration |
`getBrakingDistance(decel)` | `double` | Same formula with custom deceleration | Distance for specific braking rate |
`getTotalReactionTime()` | `double` | `0.3` [s] | Human + system reaction time |
`getThreeSecondsDistance()` | `double` | `3.0 × speed` | Swedish "3-second rule" safety margin |
`getStoppingPointForTurnRadius(R)` | `QPointF` | Arc geometry | XY position after braking on curve |

**Braking Distance Formula:**

The implementation vehicles/carstate.cpp240-253 uses:

```
d = v × t_reaction - sign(v) × 0.5 × (|v| + a_max × t_reaction)² / a_brake
```


Where:

`v`

= current speed [m/s]`t_reaction`

= 0.3s (default)`a_max`

= maximum acceleration`a_brake`

= braking deceleration (negative)**Stopping Point on Curve:**

The method `getStoppingPointForTurnRadius()`

vehicles/carstate.cpp263-266 calculates the vehicle's final position when braking while turning:

```
x = |R| × sin(d_brake / |R|)
y = R × (1 - cos(d_brake / |R|))
```


This is used for collision prediction with obstacles ahead on curved paths.

**Sources:** vehicles/carstate.cpp240-266 vehicles/carstate.h49-54

`CarState`

registers the following parameters with `ParameterServer`

:

| Parameter Name | Type | Description | Setter | Getter |
|---|---|---|---|---|
`VEH_LENGTH` | float | Vehicle length [m] | `setLength()` | `getLength()` |
`VEH_WIDTH` | float | Vehicle width [m] | `setWidth()` | `getWidth()` |
`VEH_WHLBASE` | float | Wheelbase [m] | `setAxisDistance()` | `getAxisDistance()` |
`VEH_RA2CO_X` | float | Rear axle to center offset X [m] | `setRearAxleToCenterOffset()` | `getRearAxleToCenterOffset()` |
`VEH_RA2REO_X` | float | Rear axle to rear end offset X [m] | `setRearAxleToRearEndOffset()` | `getRearAxleToRearEndOffset()` |
`PP_EGA_TYPE` | int | End goal alignment type enum | `setEndGoalAlignmentType()` | `getEndGoalAlignmentType()` |

**Sources:** vehicles/carstate.cpp314-335

The `draw()`

method vehicles/carstate.cpp32-212 renders the vehicle with:

`sigma > 0`

)**Sources:** vehicles/carstate.cpp32-212

`TruckState`

extends `CarState`

to support articulated vehicles with trailers, implementing sophisticated dynamics for both forward and reverse driving.

`TruckState`

extends `CarState`

with support for towing a `TrailerState`

via the `VehicleState::mTrailingVehicle`

member. The connection uses hitch offsets to define the articulation point.

**Truck-Trailer Coordinate System**

**Key Methods:**

| Method | Location | Description |
|---|---|---|
`setTrailingVehicle(QSharedPointer<TrailerState>)` | vehicles/truckstate.cpp116-119 | Attaches trailer to truck |
`getTrailingVehicle()` | vehicles/truckstate.cpp109-114 | Returns trailer with type cast |
`setTrailerAngle(double)` | vehicles/truckstate.cpp121-124 | Sets articulation angle |
`getTrailerAngleRadians()` | vehicles/truckstate.h33 | Returns `mTrailerAngle_deg × π/180` |

**Sources:** vehicles/truckstate.h30-35 vehicles/truckstate.cpp109-124 vehicles/vehiclestate.h

The `updateTrailingVehicleOdomPositionAndYaw()`

method vehicles/truckstate.cpp58-82 updates the trailer position and articulation angle based on the truck's motion. This is called automatically by `TruckState::updateOdomPositionAndYaw()`

.

**Trailer Update Algorithm**

**Kinematic Simulation Mode:**

When `mSimulateTrailer == true`

and using odometry position type, the articulation angle is computed using a simplified kinematic model:

```
Δθ_trailer = (drivenDistance / L_trailer) × sin(θ_hitch - θ_trailer)
θ_trailer_new = normalize(θ_trailer + Δθ_trailer)
```


Where `L_trailer = getTrailingVehicle()->getWheelBase()`

is the trailer wheelbase.

**Sensor Mode:**

When an external sensor provides the articulation angle (e.g., from encoder or IMU), the trailer yaw is computed directly:

```
θ_trailer = θ_hitch - getTrailerAngleRadians()
```


**Position Calculation:**

The trailer's rear axle position is calculated by:

`updateWithOffsetAndYawRotation()`

for the transformation**Sources:** vehicles/truckstate.cpp58-82 vehicles/truckstate.h22-23

The `getCurvatureWithTrailer()`

method vehicles/truckstate.cpp84-107 implements the core control algorithm for articulated vehicles. It computes the steering curvature needed to guide the truck-trailer combination toward a target point, with separate logic for forward and reverse driving.

**Curvature Calculation Algorithm**

**Forward Driving (Speed > 0):**

The algorithm aims the trailer directly at the target point:

**Reverse Driving (Speed < 0):**

The algorithm first computes the trailer's rear axle position in the vehicle frame, then aims from the trailer position:

The reverse calculation includes the autopilot radius term to account for the look-ahead distance used by the Pure Pursuit algorithm.

**Final Curvature:**

The base curvature includes both the trailer angle error and a stabilization term:

The division by `cos(trailerAngle)`

projects the curvature back to the truck's reference frame.

**Sources:** vehicles/truckstate.cpp84-107 vehicles/truckstate.h24-28 vehicles/truckstate.h49-50

`TruckState`

overrides key `VehicleState`

and `CarState`

methods to properly handle trailer dynamics:

**Method Override Summary**

| Method | Location | Override Behavior |
|---|---|---|
`getCurvatureToPointInVehicleFrame(point)` | vehicles/truckstate.cpp26-32 | Calls `getCurvatureWithTrailer()` if trailer attached, else `CarState::getCurvatureToPointInVehicleFrame()` |
`updateOdomPositionAndYaw(distance, type)` | vehicles/truckstate.cpp34-38 | First calls `updateTrailingVehicleOdomPositionAndYaw()` , then `CarState::updateOdomPositionAndYaw()` |
`setPosition(point)` | vehicles/truckstate.cpp40-46 | Calls `CarState::setPosition()` , then updates trailer with `updateTrailingVehicleOdomPositionAndYaw(0, ...)` |
`setLength(length)` | vehicles/truckstate.cpp20-24 | Calls `CarState::setLength()` , then sets `mRearAxleToHitchOffset = 0.1 × length` |

**Critical Ordering:**

The `updateOdomPositionAndYaw()`

override vehicles/truckstate.cpp34-38 updates the trailer *before* updating the truck position:

This ensures the trailer's articulation angle and position are computed using the truck's *current* position before the truck moves to its new position.

**Sources:** vehicles/truckstate.cpp20-46

In addition to `CarState`

parameters, `TruckState`

registers:

| Parameter Name | Type | Description |
|---|---|---|
`VEH_RA2HO_X` | float | Rear axle to hitch offset X [m] |
| (Trailer parameters) | - | Delegated to `TrailerState` if attached |

**Sources:** vehicles/truckstate.cpp126-139

The `draw()`

method vehicles/truckstate.cpp142-305 provides visualization of the truck-trailer combination with autopilot debugging overlays.

**Rendering Components:**

| Component | Color | Description |
|---|---|---|
| Truck wheels | `Qt::darkGray` (unselected) / `Qt::black` (selected) | Four wheels (rear and front axles) |
| Truck hull | Vehicle color | Rounded rectangle body |
| Front bumper | `Qt::lightGray` / `Qt::green` (selected) | Front end |
| Truck rear axle | `Qt::red` | Reference point (position origin) |
| Truck hitch | `Qt::magenta` | Articulation connection point |
| Trailer | Delegated to `TrailerState::drawTrailer()` | Full trailer rendering |
| Autopilot radius | `Qt::black` pen, 30px width | Circle around reference point |
| Alignment point | `Qt::green` | End goal alignment reference |
| Target point | `Qt::darkMagenta` | Autopilot pursuit target |

**Autopilot Visualization Logic:**

The rendering switches the reference point for autopilot visualization based on driving direction:

When reversing with a trailer, the trailer's rear axle becomes the reference point for:

This visualization matches the control logic in `getCurvatureWithTrailer()`

where the trailer rear axle is used for reverse path following.

**Status Text Display:**

The text overlay vehicles/truckstate.cpp259-303 shows:

**Sources:** vehicles/truckstate.cpp142-305 vehicles/truckstate.cpp205-208

`TrailerState`

represents a passive trailer that is towed by a `TruckState`

. Its position is computed by the towing vehicle rather than through independent odometry.

| Property | Type | Description | Default |
|---|---|---|---|
`mWheelBase` | `double` | Distance from hitch to rear axle [m] | 0.64 m |
`mAngle` | `double` | Articulation angle (public) | 0.0 |

**Default dimensions** (from Griffin trailer):

**Sources:** vehicles/trailerstate.h27-28 vehicles/trailerstate.cpp10-19

`TrailerState`

registers trailer-specific parameters:

| Parameter Name | Type | Description |
|---|---|---|
`TRLR_COMP_ID` | int | Trailer component ID |
`TRLR_LENGTH` | float | Trailer length [m] |
`TRLR_WIDTH` | float | Trailer width [m] |
`TRLR_WHLBASE` | float | Trailer wheelbase [m] |
`TRLR_RA2CO_X` | float | Rear axle to center offset X [m] |
`TRLR_RA2REO_X` | float | Rear axle to rear end offset X [m] |
`TRLR_RA2HO_X` | float | Rear axle to hitch offset X [m] |

**Sources:** vehicles/trailerstate.cpp29-52

The `updateOdomPositionAndYaw()`

method vehicles/trailerstate.cpp54-60 is intentionally a no-op:

This reflects the physical reality that trailers are passive components without independent actuation. All trailer state updates are performed by the towing vehicle through `TruckState::updateTrailingVehicleOdomPositionAndYaw()`

vehicles/truckstate.cpp58-82

The `steeringCurvatureToSteering()`

method vehicles/trailerstate.h34 is also a stub, as trailers have no active steering.

**Sources:** vehicles/trailerstate.cpp54-60 vehicles/trailerstate.h34

`TrailerState`

provides two drawing methods to support both attached and standalone trailer visualization:

**Drawing Methods**

| Method | Location | Usage | Transform Context |
|---|---|---|---|
`drawTrailer(painter, drawTrans)` | vehicles/trailerstate.cpp64-101 | Called by `TruckState::draw()` | Uses trailer's position and yaw from `getPosition()` |
`draw(painter, drawTrans, txtTrans, isSelected)` | vehicles/trailerstate.cpp103-129 | Standalone rendering | Uses `mAngle` property for articulation |

**drawTrailer() Implementation:**

Renders the trailer as part of a truck-trailer combination:

**draw() Implementation:**

Renders an unattached trailer:

The standalone version rotates by `pos.getYaw() - mAngle + 180`

to account for the articulation angle when the trailer is not attached to a truck.

**Sources:** vehicles/trailerstate.cpp64-101 vehicles/trailerstate.cpp103-129

All ground vehicle models check `mStateInitialized`

flag before rendering. This flag is set when vehicle parameters have been properly configured:

This prevents rendering vehicles with uninitialized or invalid dimensions.

**Sources:** vehicles/carstate.h29-30 vehicles/trailerstate.h41-42

The ground vehicle models provide a complete implementation of Ackermann steering kinematics with support for articulated vehicles:

| Class | Purpose | Key Features |
|---|---|---|
`CarState` | Basic Ackermann vehicle | Bicycle model odometry, steering limits, braking distance |
`TruckState` | Articulated vehicle | Trailer composition, articulation dynamics, curvature with trailer |
`TrailerState` | Passive trailer | Passive kinematics, parameter storage, rendering |

These models are used by the `PurepursuitWaypointFollower`

autopilot (see Pure Pursuit Implementation) and the `MovementController`

for direct vehicle control.

Refresh this wiki
