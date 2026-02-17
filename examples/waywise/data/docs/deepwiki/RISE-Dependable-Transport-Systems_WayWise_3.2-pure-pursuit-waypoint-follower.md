# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/3.2-pure-pursuit-waypoint-follower

The Pure Pursuit Waypoint Follower (`PurepursuitWaypointFollower`

) is the primary autopilot implementation in WayWise for autonomous route following. It implements the pure pursuit path tracking algorithm with extensions for end goal precision alignment, adaptive lookahead distance, and trailer-aware vehicle dynamics.

This document covers the pure pursuit implementation specifically. For information about the general waypoint follower interface, see Waypoint Follower Interface. For other autopilot modes like dynamic point following, see Follow Point Controller.

**Sources:** autopilot/purepursuitwaypointfollower.h1-130 autopilot/purepursuitwaypointfollower.cpp1-20

**Diagram: PurepursuitWaypointFollower System Integration**

The Pure Pursuit Waypoint Follower operates in one of two deployment modes determined at construction:

**Onboard Mode**: Constructed with a `MovementController`

, it commands the vehicle directly through steering and speed setpoints. Used when the autopilot runs on the vehicle itself.

**Remote Mode**: Constructed with a `VehicleConnection`

, it sends velocity and yaw commands over MAVLink. Used when the autopilot runs on a ground station computer controlling a remote vehicle.

**Sources:** autopilot/purepursuitwaypointfollower.cpp16-29 communication/mavsdkvehicleserver.cpp557-564

| Mode | Constructor | Control Method | Typical Use Case |
|---|---|---|---|
| Onboard | `PurepursuitWaypointFollower(QSharedPointer<MovementController>)` | `mMovementController->setDesiredSteeringCurvature()` | Vehicle-side autopilot execution |
| Remote | `PurepursuitWaypointFollower(QSharedPointer<VehicleConnection>, PosType)` | `mVehicleConnection->requestVelocityAndYaw()` | Ground station controlling remote vehicle |

The mode is checked using `isOnVehicle()`

which returns true if `mMovementController`

is not null.

**Sources:** autopilot/purepursuitwaypointfollower.h46-50 autopilot/purepursuitwaypointfollower.cpp380-411

The waypoint follower operates as a finite state machine with five primary states for route following:

**Diagram: Pure Pursuit State Machine**

| State | Enum Value | Purpose | Exit Condition |
|---|---|---|---|
`NONE` | `WayPointFollowerSTMstates::NONE` | Inactive, no route following | `startFollowingRoute()` called |
`FOLLOW_ROUTE_INIT` | `WayPointFollowerSTMstates::FOLLOW_ROUTE_INIT` | Initialize route following, set first waypoint as goal | Immediately transitions next cycle |
`FOLLOW_ROUTE_GOTO_BEGIN` | `WayPointFollowerSTMstates::FOLLOW_ROUTE_GOTO_BEGIN` | Navigate to route start in straight line | First waypoint enters lookahead circle |
`FOLLOW_ROUTE_FOLLOWING` | `WayPointFollowerSTMstates::FOLLOW_ROUTE_FOLLOWING` | Main route following with pure pursuit | Last waypoint becomes current target |
`FOLLOW_ROUTE_APPROACHING_END_GOAL` | `WayPointFollowerSTMstates::FOLLOW_ROUTE_APPROACHING_END_GOAL` | Precision alignment to final goal | Alignment threshold met or overshoot detected |
`FOLLOW_ROUTE_FINISHED` | `WayPointFollowerSTMstates::FOLLOW_ROUTE_FINISHED` | Route complete, cleanup | Immediately transitions to `NONE` |

**Sources:** autopilot/purepursuitwaypointfollower.h21-35 autopilot/purepursuitwaypointfollower.cpp183-378

The state machine runs on a timer with period `mUpdateStatePeriod_ms`

(default 50ms = 20Hz). The `updateState()`

method is called on each timer tick and executes the logic for the current state.

**Sources:** autopilot/purepursuitwaypointfollower.h115-116 autopilot/purepursuitwaypointfollower.cpp20-21 autopilot/purepursuitwaypointfollower.cpp147

**Diagram: Pure Pursuit Algorithm Flow**

The algorithm uses different reference positions depending on vehicle configuration and direction:

| Condition | Reference Position | Rationale |
|---|---|---|
| Forward motion (speed ≥ 0) | Vehicle rear axle | Standard bicycle model reference |
| Backward motion (speed < 0) without trailer | Vehicle rear axle | Same as forward |
| Backward motion (speed < 0) with trailer | Trailer rear axle | Trailer dictates path when reversing |

**Sources:** autopilot/purepursuitwaypointfollower.cpp50-59

The algorithm searches for intersections between a circle centered at the vehicle reference position (radius = lookahead distance) and line segments formed by consecutive waypoints:

**Diagram: Lookahead Circle Intersection Search**

The search processes waypoints backward through the lookahead window (`numWaypointsLookahead = 8`

waypoints) to find the furthest intersection point, which provides maximum progress along the route.

**Sources:** autopilot/purepursuitwaypointfollower.cpp237-260

| Number of Intersections | Action |
|---|---|
| 0 | Reuse previous goal (vehicle has left the route, e.g., due to high speed) |
| 1 | Use the single intersection as goal |
| 2 | Select intersection closer to the current waypoint (more progress along route) |

When two intersections exist, the algorithm chooses the one with minimum distance to `waypoint[i]`

(the current target waypoint).

**Sources:** autopilot/purepursuitwaypointfollower.cpp262-292

Speed is linearly interpolated based on goal position between waypoints:

```
interpolatedSpeed = lastWaypoint.speed + (nextWaypoint.speed - lastWaypoint.speed) * (x / d)
where:
x = distance from lastWaypoint to goal
d = distance from lastWaypoint to nextWaypoint
```


**Sources:** autopilot/purepursuitwaypointfollower.cpp458-466

The lookahead radius can operate in two modes:

| Mode | Configuration | Formula | Use Case |
|---|---|---|---|
| Fixed | `mCurrentState.adaptivePurePursuitRadius = false` | `radius = mCurrentState.purePursuitRadius` | Constant lookahead, predictable behavior |
| Adaptive | `mCurrentState.adaptivePurePursuitRadius = true` | `radius = max(purePursuitRadius, adaptiveCoefficient × speed)` | Speed-dependent lookahead, smoother high-speed tracking |

The adaptive coefficient is typically set to 1.0 (one second lookahead), meaning at 5 m/s, the radius is at least 5 meters.

**Sources:** autopilot/purepursuitwaypointfollower.cpp478-491 autopilot/purepursuitwaypointfollower.h27-29

| Parameter Name | Type | Getter | Setter | Description |
|---|---|---|---|---|
`PP_RADIUS` | float | `getPurePursuitRadius()` | `setPurePursuitRadius()` | Base lookahead radius in meters |
`PP_ARC` | float | `getAdaptivePurePursuitRadiusCoefficient()` | `setAdaptivePurePursuitRadiusCoefficient()` | Adaptive radius coefficient (seconds) |

These parameters are registered with `ParameterServer`

and can be modified at runtime via MAVLink.

**Sources:** autopilot/purepursuitwaypointfollower.cpp31-37

When approaching the final waypoint, the follower transitions to `FOLLOW_ROUTE_APPROACHING_END_GOAL`

state, which implements precision alignment. Three alignment types determine which point on the vehicle should align with the goal:

**Diagram: End Goal Alignment Reference Points**

**Sources:** autopilot/purepursuitwaypointfollower.cpp503-528 vehicles/carstate.cpp108-124

| Type | Enum Value | Reference Point Calculation | Typical Use Case |
|---|---|---|---|
`REAR_AXLE` | 0 | `vehicleState->getPosition(posType)` | Default, simple alignment |
`CENTER` | 1 | `posInVehicleFrameToPosPointENU(rearAxleToCenterOffset)` | Center of vehicle at goal |
`FRONT_REAR_END` | 2 | Forward: `rearAxleToRearEndOffset + {length, 0, 0}` Reverse: `rearAxleToRearEndOffset` | Precise docking scenarios |

The alignment type is configured via parameter `PP_EGA_TYPE`

(Pure Pursuit End Goal Alignment Type).

**Sources:** vehicles/carstate.cpp331-334

When not yet aligned, the algorithm extends the goal backward along the previous route segment to maintain the lookahead radius:

```
extensionDistance = max(purePursuitRadius - distanceToGoal, 0)
extensionRatio = -extensionDistance / distanceToPreviousWaypoint
extendedGoal = endGoalToPreviousWaypointLine.pointAt(extensionRatio)
```


If adaptive approach speed is enabled (`mAdaptiveApproachSpeedEnabled = true`

):

```
adaptiveSpeed = ((purePursuitRadius - extensionDistance) / purePursuitRadius) × endGoalSpeed
adaptiveSpeed = clamp(adaptiveSpeed, minApproachSpeed, endGoalSpeed)
```


This gradually reduces speed as the vehicle approaches the goal, but maintains a minimum approach speed for controllability.

**Sources:** autopilot/purepursuitwaypointfollower.cpp345-365

The algorithm detects overshoot by checking if the vehicle has passed the goal:

```
angleBetweenLines = endGoalToReferencePoint.angleTo(endGoalToPreviousWaypoint)
hasOvershotEndGoal = abs(angleBetweenLines) > 90°
```


If overshoot is detected and `mRetryAfterEndGoalOvershot = false`

, the follower stops. Otherwise, it continues trying to reach the goal.

**Sources:** autopilot/purepursuitwaypointfollower.cpp332-344

Routes can be added in two ways:

**1. Inactive Mode (follower stopped):**

Simply appends the new route to the existing waypoint list.

**2. Active Mode (follower running):**

Truncates the current route at the current waypoint and merges the new route starting from its closest point to the vehicle.

**Sources:** autopilot/purepursuitwaypointfollower.cpp88-116

Setting `mCurrentState.repeatRoute = true`

enables continuous route following:

`FOLLOW_ROUTE_APPROACHING_END_GOAL`

, when alignment threshold is met, transitions back to `FOLLOW_ROUTE_INIT`

instead of `FOLLOW_ROUTE_FINISHED`

`lookaheadEndIndex % mWaypointList.size()`

`currentWaypointIndex = (i + currentWaypointIndex - 1) % mWaypointList.size()`

**Sources:** autopilot/purepursuitwaypointfollower.cpp238-245 autopilot/purepursuitwaypointfollower.cpp317-322

| fromBeginning | Behavior |
|---|---|
`true` | Start from waypoint[0], transition through `FOLLOW_ROUTE_GOTO_BEGIN` |
`false` | Find closest waypoint to current position, start from there in `FOLLOW_ROUTE_FOLLOWING` or `FOLLOW_ROUTE_APPROACHING_END_GOAL` |

**Sources:** autopilot/purepursuitwaypointfollower.cpp118-148

The follower supports geofenced speed limits defined in GeoJSON format:

**Diagram: Speed Limit Region Processing Pipeline**

**Sources:** autopilot/purepursuitwaypointfollower.cpp542-672

The expected format is a WGS-84 GeoJSON FeatureCollection:

**Sources:** autopilot/purepursuitwaypointfollower.cpp600-672

Speed limits are applied in `updateControl()`

:

Multiple overlapping regions apply the most restrictive (minimum) speed limit.

**Sources:** autopilot/purepursuitwaypointfollower.cpp380-411 autopilot/purepursuitwaypointfollower.cpp542-557

The polygon is automatically closed if the first and last points differ.

**Sources:** autopilot/purepursuitwaypointfollower.h37-40

When a `TruckState`

has a trailing `TrailerState`

, curvature calculations account for multi-body dynamics:

**Diagram: Trailer-Aware Reference Position and Curvature**

**Sources:** vehicles/truckstate.cpp26-32 vehicles/truckstate.cpp84-107

For reverse motion with a trailer, the algorithm implements a feedback controller:

**Sources:** vehicles/truckstate.cpp84-107

The trailer position is updated in `TruckState::updateTrailingVehicleOdomPositionAndYaw()`

:

`truckHitchPosition = posInVehicleFrameToPosPointENU(rearAxleToHitchOffset)`

`mSimulateTrailer = true`

for odometry):
`trailerPosition = truckHitchPosition - trailerHitchToRearAxleOffset`

**Sources:** vehicles/truckstate.cpp58-82

| Parameter | Purpose | Typical Value |
|---|---|---|
`mPurePursuitForwardGain` | Curvature gain for forward motion (not used with trailer) | 1.0 |
`mPurePursuitReverseGain` | Curvature gain for reverse motion with trailer | -1.0 |

These gains are vehicle-specific and stored in `TruckState`

.

**Sources:** vehicles/truckstate.h49-50 vehicles/truckstate.cpp92-103

When operating on the vehicle (`isOnVehicle() == true`

):

The curvature is calculated by `VehicleState::getCurvatureToPointInENU()`

which calls the vehicle-specific implementation (`CarState`

or `TruckState`

).

**Sources:** autopilot/purepursuitwaypointfollower.cpp392-397

When operating from a ground station (`isOnVehicle() == false`

):

This sends a velocity vector pointing toward the goal with magnitude equal to desired speed, plus a yaw setpoint aligned with the direction of travel.

**Sources:** autopilot/purepursuitwaypointfollower.cpp399-410

For flying vehicles (remote mode), the algorithm overrides altitude from waypoints:

This is set at route start and maintains constant altitude, ignoring waypoint height specifications. The z-component of velocity is calculated to maintain this altitude.

**Sources:** autopilot/purepursuitwaypointfollower.cpp127-128 autopilot/purepursuitwaypointfollower.cpp402

**Diagram: Emergency Brake Signal Flow**

The emergency brake is activated when route following starts and deactivated when it stops:

**Sources:** autopilot/purepursuitwaypointfollower.cpp126 autopilot/purepursuitwaypointfollower.cpp172

`MavsdkVehicleServer`

bridges MAVLink mission messages to the waypoint follower:

Mission items are converted from MAVLink `MISSION_ITEM_INT`

format (frame: `MAV_FRAME_LOCAL_ENU`

):

**Sources:** communication/mavsdkvehicleserver.cpp105-121 communication/mavsdkvehicleserver.cpp578-592

The server listens for MAVLink flight mode changes:

| Flight Mode | Action |
|---|---|
`Mission` | `emit startWaypointFollower(false)` - Start from closest point |
`Offboard` | `emit startFollowPoint()` - Switch to FollowPoint mode |
| Other | Pause waypoint follower if active |

**Sources:** communication/mavsdkvehicleserver.cpp80-103

The follower can track using different position sources:

| PosType | Description | Use Case |
|---|---|---|
`PosType::fused` | Sensor-fused position (GNSS + IMU + odom) | Default, most accurate |
`PosType::GNSS` | Raw GNSS position | GNSS-only operation |
`PosType::odom` | Odometry-based position | Indoor/GPS-denied |
`PosType::IMU` | IMU-based position | Short-term dead reckoning |
`PosType::UWB` | Ultra-wideband positioning | Indoor precise positioning |

**Sources:** autopilot/purepursuitwaypointfollower.h110 autopilot/purepursuitwaypointfollower.cpp413-421

| Parameter | Type | Default | Description | Config Key |
|---|---|---|---|---|
| Pure Pursuit Radius | float | 1.0 m | Base lookahead distance | `PP_RADIUS` |
| Adaptive Coefficient | float | 1.0 s | Speed-to-radius multiplier | `PP_ARC` |
| Adaptive Radius Enabled | bool | false | Enable speed-dependent lookahead | - |
| Repeat Route | bool | false | Loop route continuously | - |
| End Goal Alignment Type | int | 0 (REAR_AXLE) | Reference point for final alignment | `PP_EGA_TYPE` |
| End Goal Alignment Threshold | float | 0.1 m | Distance threshold for completion | - |
| Retry After Overshoot | bool | false | Continue if goal is overshot | - |
| Adaptive Approach Speed | bool | false | Reduce speed near goal | - |
| Min Approach Speed | float | 0.0 m/s | Minimum speed when approaching goal | - |

**Sources:** autopilot/purepursuitwaypointfollower.h27-126 autopilot/purepursuitwaypointfollower.cpp31-37

| Field | Type | Default | Description |
|---|---|---|---|
`mUpdateStatePeriod_ms` | unsigned | 50 ms | State machine update rate (20 Hz) |
`numWaypointsLookahead` | int | 8 | Number of waypoints in lookahead window |

**Sources:** autopilot/purepursuitwaypointfollower.h31-115

The `WayPointFollowerState`

structure maintains all runtime state:

**Sources:** autopilot/purepursuitwaypointfollower.h22-35

| Method | Return Type | Description |
|---|---|---|
`getCurrentGoal()` | `const PosPoint` | Current pursuit goal point |
`getCurrentRoute()` | `QList<PosPoint>` | Complete waypoint list |
`getCurrentState()` | `WayPointFollowerState` | Full state structure |
`isActive()` | `bool` | Whether follower is running |

**Sources:** autopilot/purepursuitwaypointfollower.h66-88

The `distanceOfRouteLeft`

signal is emitted each update cycle with the remaining route distance calculated from the current position through all remaining waypoints.

**Sources:** autopilot/purepursuitwaypointfollower.h99-100 autopilot/purepursuitwaypointfollower.cpp468-476

Refresh this wiki
