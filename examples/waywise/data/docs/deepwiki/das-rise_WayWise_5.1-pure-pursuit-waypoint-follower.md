# Source: https://deepwiki.com/das-rise/WayWise/5.1-pure-pursuit-waypoint-follower

The `PurepursuitWaypointFollower`

is a core autopilot implementation in WayWise that enables a vehicle to follow a predefined list of waypoints using the Pure Pursuit algorithm. It supports both local execution (directly controlling a `MovementController`

) and remote execution (sending commands via a `VehicleConnection`

).

The follower operates on a 50ms update loop autopilot/purepursuitwaypointfollower.h115-116 calculating the required steering curvature and speed to reach a "look-ahead" point on the path. It manages a internal state machine to handle the lifecycle of route following, from initialization to reaching the final goal.

`MovementController`

for on-vehicle control or a `VehicleConnection`

for remote operation autopilot/purepursuitwaypointfollower.cpp16-29`QTimer`

triggers `updateState()`

every 50ms autopilot/purepursuitwaypointfollower.cpp20-21`PosType::fused`

by default but can be configured to use specific positioning sources like GNSS or UWB autopilot/purepursuitwaypointfollower.h110**Sources:** autopilot/purepursuitwaypointfollower.h42-127 autopilot/purepursuitwaypointfollower.cpp16-30

The follower's behavior is governed by the `WayPointFollowerSTMstates`

enum, which tracks the progression along the route.

| State | Description |
|---|---|
`NONE` | Idle state, no route active autopilot/purepursuitwaypointfollower.h21 |
`FOLLOW_ROUTE_INIT` | Initializing the route following sequence autopilot/purepursuitwaypointfollower.h21 |
`FOLLOW_ROUTE_GOTO_BEGIN` | Navigating from current position to the start of the route autopilot/purepursuitwaypointfollower.h21 |
`FOLLOW_ROUTE_FOLLOWING` | Actively pursuing waypoints in the middle of the route autopilot/purepursuitwaypointfollower.h21 |
`FOLLOW_ROUTE_APPROACHING_END_GOAL` | Reducing speed or adjusting behavior as the final waypoint nears autopilot/purepursuitwaypointfollower.h21 |
`FOLLOW_ROUTE_FINISHED` | Route completed; vehicle transitions to a hold or stop state autopilot/purepursuitwaypointfollower.h21 |

**Sources:** autopilot/purepursuitwaypointfollower.h21 autopilot/purepursuitwaypointfollower.cpp130-145

The "look-ahead distance" is the most critical parameter in Pure Pursuit. WayWise supports two modes:

`PP_RADIUS`

) used to find the target point on the path autopilot/purepursuitwaypointfollower.cpp34`PP_ARC`

), allowing for stability at high speeds and precision at low speeds autopilot/purepursuitwaypointfollower.cpp35The look-ahead point is determined by finding the intersection of a circle (centered at the vehicle) with the line segments of the route autopilot/purepursuitwaypointfollower.cpp75-80

**Sources:** autopilot/purepursuitwaypointfollower.cpp31-37 autopilot/purepursuitwaypointfollower.h27-29

The follower does not simply jump between waypoint speeds. It performs **interpolated speed** calculations to ensure smooth transitions between segments.

`getInterpolatedSpeed()`

function calculates the target speed based on the vehicle's progress between the `lastWaypoint`

and the `nextWaypoint`

autopilot/purepursuitwaypointfollower.h79`setAdaptiveApproachSpeedEnabled()`

, the vehicle will decelerate as it approaches the final goal, respecting a `mMinApproachSpeed`

autopilot/purepursuitwaypointfollower.h90-91**Sources:** autopilot/purepursuitwaypointfollower.h79-91 autopilot/purepursuitwaypointfollower.cpp183-200

The follower can enforce regional speed limits defined in GeoJSON files.

`SpeedLimitRegion`

structures containing a 2D-Polygon boundary and a `maxSpeed`

autopilot/purepursuitwaypointfollower.h37-40`updateState`

loop and caps the target speed accordingly autopilot/purepursuitwaypointfollower.cpp93-97**Sources:** autopilot/purepursuitwaypointfollower.h37-40 autopilot/purepursuitwaypointfollower.h93-97

This diagram illustrates how the `PurepursuitWaypointFollower`

interacts with the broader WayWise ecosystem, specifically how it receives missions via MAVLink and translates them into movement.

**Sources:** communication/mavsdkvehicleserver.cpp105-121 autopilot/purepursuitwaypointfollower.cpp16-21 autopilot/purepursuitwaypointfollower.cpp183-185

This diagram maps the natural language concepts of "Route Following" to the specific C++ classes and members.

**Sources:** autopilot/purepursuitwaypointfollower.h42-127 communication/mavsdkvehicleserver.h24-71 autopilot/purepursuitwaypointfollower.h22-35

When the vehicle reaches the final waypoint, the follower handles alignment based on the `mEndGoalAlignmentThreshold`

.

`mRetryAfterEndGoalOvershot`

is true, the vehicle will attempt to maneuver back to the exact goal if it passes it autopilot/purepursuitwaypointfollower.h58-59`getVehicleAlignmentReferencePosPoint()`

autopilot/purepursuitwaypointfollower.cpp50-59**Sources:** autopilot/purepursuitwaypointfollower.h58-62 autopilot/purepursuitwaypointfollower.cpp50-59

Refresh this wiki

This wiki was recently refreshed. Please wait 7 days to refresh again.