# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/3-autopilot-systems

This page documents the autopilot components in WayWise that enable autonomous vehicle navigation. Autopilots implement algorithms for following waypoints, tracking dynamic targets, and coordinating with safety systems. For information about sensor positioning that feeds autopilot algorithms, see Sensor Integration. For details on route planning and waypoint generation, see Route Planning & Utilities.

WayWise autopilot systems are built on a dual-deployment architecture where autopilot controllers can run either:

`MovementController`

for local control (lower latency, ~50ms update rate)`VehicleConnection`

to control a remote vehicle (higher latency, ~1000ms update rate)All autopilot implementations inherit from the `WaypointFollower`

abstract interface, which defines a standard contract for route following, starting/stopping, and emergency brake coordination.

**High-Level Autopilot Architecture:**

**Sources:** autopilot/waypointfollower.h1-41 autopilot/purepursuitwaypointfollower.h42-128 autopilot/followpoint.h39-98 autopilot/multiwaypointfollower.h17-66

The `WaypointFollower`

abstract class (autopilot/waypointfollower.h14-38) defines the standard interface that all autopilot implementations must satisfy:

| Method | Purpose |
|---|---|
`addWaypoint(PosPoint)` | Add a single waypoint to the route |
`addRoute(QList<PosPoint>)` | Add a list of waypoints |
`clearRoute()` | Remove all waypoints |
`startFollowingRoute(bool fromBeginning)` | Activate the autopilot |
`stop()` | Deactivate and hold position |
`resetState()` | Reset internal state machine |
`isActive()` | Check if autopilot is running |
`getCurrentGoal()` | Get the current target point |
`getCurrentRoute()` | Get the full route |
`getRepeatRoute()` / `setRepeatRoute(bool)` | Enable route looping |

**Emergency Brake Coordination:**

The interface defines two signals for coordinating with the `EmergencyBrake`

safety system (autopilot/waypointfollower.h35-37):

`activateEmergencyBrake()`

- Emitted when autopilot starts, enabling safety monitoring`deactivateEmergencyBrake()`

- Emitted when autopilot stops, disabling monitoring**Sources:** autopilot/waypointfollower.h1-41

The `PurepursuitWaypointFollower`

class (autopilot/purepursuitwaypointfollower.cpp1-673) is the primary autopilot implementation, using the **pure pursuit algorithm** for smooth path tracking. It is the most sophisticated autopilot with support for trailer-aware curvature calculations, speed limit regions, and adaptive approach speeds.

The autopilot operates as a state machine with five distinct states:

**Sources:** autopilot/purepursuitwaypointfollower.cpp183-378 autopilot/purepursuitwaypointfollower.h21-35

The core algorithm (autopilot/purepursuitwaypointfollower.cpp222-305) works as follows:

`numWaypointsLookahead`

waypoints ahead (default: 8) to find where a circle of radius `purePursuitRadius`

intersects the route`purePursuitRadius`

**Key Parameters:**

| Parameter | Default | Description |
|---|---|---|
`mCurrentState.purePursuitRadius` | 1.0m | Base lookahead radius |
`mCurrentState.adaptivePurePursuitRadiusCoefficient` | 1.0 | Speed multiplier when adaptive mode enabled |
`mCurrentState.numWaypointsLookahead` | 8 | How many waypoints to search ahead |
`mEndGoalAlignmentThreshold` | 0.1m | Distance threshold for goal completion |

**Sources:** autopilot/purepursuitwaypointfollower.cpp222-305 autopilot/purepursuitwaypointfollower.cpp458-466

When `mCurrentState.adaptivePurePursuitRadius`

is enabled (autopilot/purepursuitwaypointfollower.cpp478-491), the lookahead radius dynamically adjusts:

```
dynamicRadius = adaptivePurePursuitRadiusCoefficient * vehicleSpeed
purePursuitRadius = max(dynamicRadius, basePurePursuitRadius)
```


This provides better path tracking at higher speeds by looking further ahead.

**Sources:** autopilot/purepursuitwaypointfollower.cpp478-491

The `FOLLOW_ROUTE_APPROACHING_END_GOAL`

state (autopilot/purepursuitwaypointfollower.cpp307-367) implements precise goal reaching:

**Extension Strategy**: If the vehicle is not yet aligned with the end goal, the goal is extended backwards along the route by `max(radius - distanceToGoal, 0)`

. This prevents oscillation as the vehicle approaches.

**Alignment Reference Point**: The alignment point depends on `VehicleState::getEndGoalAlignmentType()`

:

`REAR_AXLE`

: Use rear axle position (default)`CENTER`

: Use vehicle center`FRONT_REAR_END`

: Use rear end when backing, front end when forward**Overshoot Detection**: Calculates angle between (goal→vehicle) and (goal→previousWaypoint). If angle > 90°, the vehicle has overshot.

**Adaptive Approach Speed**: If `mAdaptiveApproachSpeedEnabled`

is true:

```
adaptiveSpeed = (radius - extension) / radius * goalSpeed
adaptiveSpeed = max(adaptiveSpeed, mMinApproachSpeed) // if forward
adaptiveSpeed = min(adaptiveSpeed, -mMinApproachSpeed) // if reverse
```


**Sources:** autopilot/purepursuitwaypointfollower.cpp307-367 autopilot/purepursuitwaypointfollower.cpp503-540

When the vehicle has a trailing vehicle (truck-trailer configuration), the autopilot adjusts reference points:

`getCurvatureToPointInENU()`

method automatically accounts for trailer dynamics when backingThis ensures smooth backing maneuvers with trailers.

**Sources:** autopilot/purepursuitwaypointfollower.cpp50-59 autopilot/purepursuitwaypointfollower.cpp530-540

The autopilot supports geofenced speed limits (autopilot/purepursuitwaypointfollower.cpp542-672). Speed limit regions are defined as 2D polygons in ENU coordinates with a maximum speed.

**GeoJSON Loading:**

Speed limits can be loaded from a GeoJSON file (autopilot/purepursuitwaypointfollower.cpp570-598):

`FeatureCollection`

with WGS-84 coordinates`Polygon`

(MultiPolygon not supported)`properties.maxSpeed`

field in km/h**Speed Capping:**

During control updates (autopilot/purepursuitwaypointfollower.cpp380-411), the autopilot checks if the vehicle is inside any speed limit regions. If multiple regions overlap, the most restrictive (minimum) speed limit applies:

**Sources:** autopilot/purepursuitwaypointfollower.cpp380-411 autopilot/purepursuitwaypointfollower.cpp542-672

The `addRoute()`

method (autopilot/purepursuitwaypointfollower.cpp88-116) supports dynamic route updates while the autopilot is active:

`currentWaypointIndex`

`FOLLOW_ROUTE_FOLLOWING`

or `FOLLOW_ROUTE_APPROACHING_END_GOAL`

as appropriateThis enables seamless route switching without stopping the autopilot.

**Sources:** autopilot/purepursuitwaypointfollower.cpp88-116

The `FollowPoint`

class (autopilot/followpoint.cpp1-229) implements dynamic target tracking for "follow-me" scenarios. Unlike waypoint following, this requires continuous position updates from the target being followed.

**Sources:** autopilot/followpoint.cpp135-168 autopilot/followpoint.h20-35

The FollowPoint controller requires continuous updates to prevent runaway behavior:

`updatePointToFollowInVehicleFrame()`

or `updatePointToFollowInEnuFrame()`

(autopilot/followpoint.cpp94-117)`mFollowPointHeartbeatTimer`

) is reset on each update (autopilot/followpoint.cpp119-133)`stopFollowPoint()`

is automatically called (autopilot/followpoint.cpp52-57)**Sources:** autopilot/followpoint.cpp44-133

FollowPoint supports two coordinate frames:

**Vehicle Frame** (autopilot/followpoint.cpp94-105):

`autopilotRadius`

) with line from vehicle to point**ENU Frame** (autopilot/followpoint.cpp107-117):

```
targetX = point.x + followPointDistance * cos(point.yaw + followPointAngleInDeg)
targetY = point.y + followPointDistance * sin(point.yaw + followPointAngleInDeg)
targetZ = point.height + followPointHeight
```


**Parameters:**

| Parameter | On-Vehicle Default | Remote Default | Description |
|---|---|---|---|
`followPointDistance` | 2.0m | 2.0m | Desired distance to target |
`followPointMaximumDistance` | 100m | 100m | Maximum allowed distance (safety) |
`followPointSpeed` | 1.0 m/s | N/A | Speed for ground vehicles |
`autopilotRadius` | 1.0m | 1.0m | Radius for holding position |
`followPointHeight` | 3.0m | 3.0m | Height offset for drones |
`followPointAngleInDeg` | 180° | 180° | Angle offset (0=forward, 180=behind) |

**Sources:** autopilot/followpoint.cpp11-30 autopilot/followpoint.cpp94-117 autopilot/followpoint.h22-35

The `MultiWaypointFollower`

class (autopilot/multiwaypointfollower.cpp1-161) manages multiple `WaypointFollower`

instances, enabling route switching. This is useful for vehicles that need to switch between different autopilot algorithms or routes without stopping.

MultiWaypointFollower implements the `WaypointFollower`

interface by delegating all calls to the active follower:

**Key Methods:**

| Method | Implementation |
|---|---|
`addWaypointFollower()` | Adds a follower to `mWaypointFollowerList` , returns its ID |
`setActiveWaypointFollower(int id)` | Sets `mActiveWaypointFollowerID` |
`getActiveWaypointFollower()` | Returns the active follower |
| All WaypointFollower methods | Delegated to `mWaypointFollowerList[mActiveWaypointFollowerID]` |

**Special Handling for PurepursuitWaypointFollower:**

The class provides direct access to PurePursuit-specific parameters (autopilot/multiwaypointfollower.cpp67-108) by dynamically casting to `PurepursuitWaypointFollower`

:

`setPurePursuitRadius()`

- Sets radius on all PurePursuit followers in the list`setAdaptivePurePursuitRadiusCoefficient()`

- Sets coefficient on all PurePursuit followers`getPurePursuitRadius()`

/ `getAdaptivePurePursuitRadiusCoefficient()`

- Gets from active follower**Sources:** autopilot/multiwaypointfollower.cpp1-161 autopilot/multiwaypointfollower.h17-66

The `EmergencyBrake`

class (autopilot/emergencybrake.cpp1-44) provides a safety overlay that can stop the vehicle when obstacles are detected. Autopilots coordinate with this system through signals.

**Sources:** autopilot/emergencybrake.h15-21

**Sensor Integration:**

The EmergencyBrake receives sensor inputs through slots (autopilot/emergencybrake.cpp23-34):

`brakeForDetectedCameraObject(PosPoint)`

- Object position in vehicle frame`brakeForObjectAtDistance`

(default 10m), sets brake flag**Decision Fusion:**

The `fuseSensorsAndTakeBrakeDecision()`

method (autopilot/emergencybrake.cpp36-43) combines sensor inputs:

Currently only camera objects trigger braking. The structure supports future multi-sensor fusion logic.

**Sources:** autopilot/emergencybrake.cpp1-44 autopilot/emergencybrake.h1-43

Autopilots integrate with the vehicle through two different paths depending on deployment location.

**Key Integration Points:**

**Flight Mode Subscription** (communication/mavsdkvehicleserver.cpp80-103):

`Mission`

mode → `emit startWaypointFollower(false)`

`Offboard`

mode → `emit startFollowPoint()`

**Mission Upload** (communication/mavsdkvehicleserver.cpp105-121):

`subscribe_incoming_mission()`

receives waypoints`MissionItem`

to `PosPoint`

(communication/mavsdkvehicleserver.cpp578-592)`mWaypointFollower->addRoute(route)`

**Manual Control** (communication/mavsdkvehicleserver.cpp594-608):

`MANUAL_CONTROL`

messages**Sources:** communication/mavsdkvehicleserver.cpp80-121 communication/mavsdkvehicleserver.cpp556-608

**Key Differences from On-Vehicle:**

`requestVelocityAndYaw()`

instead of `setDesiredSpeed()`

/`setDesiredSteering()`

`requestGotoENU()`

for position targets**Pure Pursuit Remote Control** (autopilot/purepursuitwaypointfollower.cpp398-410):

This calculates a velocity vector that points toward the goal with magnitude equal to the desired speed.

**Sources:** autopilot/purepursuitwaypointfollower.cpp398-410 autopilot/followpoint.cpp86-91

The `VehicleServer`

abstract class (communication/vehicleserver.h19-64) defines the interface for connecting autopilots to communication systems:

| Method | Purpose |
|---|---|
`setWaypointFollower()` | Provide WaypointFollower instance to server |
`setFollowPoint()` | Provide FollowPoint instance to server |
`setMovementController()` | Provide MovementController instance to server |

**Signals:**

`startWaypointFollower(bool fromBeginning)`

- Emitted when flight mode changes to Mission`pauseWaypointFollower()`

- Emitted when flight mode changes away from Mission`resetWaypointFollower()`

- Emitted when mission current item set to 0`clearRouteOnWaypointFollower()`

- Emitted when mission cleared`startFollowPoint()`

- Emitted when flight mode changes to Offboard`stopFollowPoint()`

- Emitted when flight mode changes away from OffboardThese signals connect MAVLink protocol events to autopilot lifecycle methods.

**Sources:** communication/vehicleserver.h1-64 communication/mavsdkvehicleserver.cpp557-576

Autopilot parameters are exposed through the `ParameterServer`

system (see Parameter Server) for runtime configuration.

**PurepursuitWaypointFollower Parameters** (autopilot/purepursuitwaypointfollower.cpp31-37):

`PP_RADIUS`

- Base pure pursuit radius (meters)`PP_ARC`

- Adaptive radius coefficient (dimensionless)**FollowPoint Parameters** (autopilot/followpoint.cpp32-42):

`FP{id}_DIST`

- Follow distance (meters)`FP{id}_MAX_DIST`

- Maximum allowed distance (meters)`FP{id}_HEIGHT`

- Height offset for drones (meters)`FP{id}_ANGLE_DEG`

- Angular offset in degrees**MultiWaypointFollower Parameters** (autopilot/multiwaypointfollower.cpp120-135):

`PP{id}_RADIUS`

- Radius for follower with ID`PP{id}_ARC`

- Adaptive coefficient for follower with IDParameters can be modified at runtime via `VehicleParameterUI`

(see Parameter Configuration UI) and are synchronized over MAVLink.

**Sources:** autopilot/purepursuitwaypointfollower.cpp31-37 autopilot/followpoint.cpp32-42 autopilot/multiwaypointfollower.cpp120-135

Refresh this wiki
