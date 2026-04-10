# Source: https://deepwiki.com/das-rise/WayWise/5.2-follow-point-and-multi-waypoint-follower

This section details the specialized autopilot implementations within the WayWise library that handle dynamic target tracking, waypoint management across multiple followers, and high-level "goto" command sequencing for aerial vehicles.

The `FollowPoint`

class is designed for dynamic target tracking, such as following a person or another vehicle where the target coordinates are continuously updated. It supports two modes of operation: **Local** (directly controlling a `MovementController`

on the vehicle) and **Remote** (sending commands via a `VehicleConnection`

from a ground station).

`FollowPoint`

utilizes a state machine defined by `FollowPointSTMstates`

autopilot/followpoint.h20 The logic is driven by a periodic timer (`mUpdateStateTimer`

) which defaults to 50ms for local operation and 1000ms for remote operation autopilot/followpoint.cpp25-30

| State | Description |
|---|---|
`NONE` | Uninitialized or inactive state. |
`FOLLOWING` | Actively moving towards the target point. |
`WAITING` | Target point reached (within the defined radius); vehicle pauses until target moves. |

To ensure safety during dynamic tracking, `FollowPoint`

implements a heartbeat watchdog autopilot/followpoint.cpp50-57 If the target point is not updated within a specific timeout (defaulting to 1000ms or 3000ms depending on mode), the system automatically stops the vehicle and activates the emergency brake autopilot/followpoint.cpp52-56

When tracking in the vehicle frame, `FollowPoint`

calculates an intersection between a line to the target and a circle defined by the `autopilotRadius`

autopilot/followpoint.cpp102-103 This ensures the steering curvature is calculated towards a point at a consistent look-ahead distance, stabilizing the approach.

The following diagram illustrates how `FollowPoint`

interacts with vehicle hardware or remote connections.

**FollowPoint Control Flow**

**Sources:**

`MultiWaypointFollower`

acts as a container and proxy for multiple `WaypointFollower`

instances. This allows the system to maintain several distinct routes or following behaviors (e.g., one `PurepursuitWaypointFollower`

for a main route and another for a return path) and switch between them dynamically.

The class maintains a `QList`

of followers and an `mActiveWaypointFollowerID`

autopilot/multiwaypointfollower.h60-62 All standard `WaypointFollower`

interface calls (like `startFollowingRoute`

, `addWaypoint`

, or `stop`

) are forwarded to the currently active instance autopilot/multiwaypointfollower.cpp24-60

`MultiWaypointFollower`

serves as a bridge to the `ParameterServer`

. It can register parameters for all contained followers, using a naming convention that includes the follower's ID (e.g., `PP0_RADIUS`

, `PP1_RADIUS`

) autopilot/multiwaypointfollower.cpp126-135

**MultiWaypointFollower Architecture**

**Sources:**

`GotoWaypointFollower`

is an implementation of the `WaypointFollower`

interface specifically designed for vehicles that accept high-level "Goto" commands, such as multicopters via MAVLink.

Unlike the Pure Pursuit follower which calculates steering curvatures, this follower manages a sequence of points and relies on the vehicle's internal flight controller to navigate between them.

`GotoWayPointFollowerSTMstates`

autopilot/gotowaypointfollower.h16`waypointProximity`

distance (default 3.0m) of the current goal autopilot/gotowaypointfollower.cpp135-140`mUpdateWaypointPeriod_ms`

) at each waypoint before proceeding to the next autopilot/gotowaypointfollower.cpp142-160In `FlyUI`

, when a user provides a route for a drone, the system automatically instantiates a `GotoWaypointFollower`

and attaches it to the `VehicleConnection`

userinterface/flyui.cpp142-143

**GotoWaypointFollower Logic**

**Sources:**

Refresh this wiki

This wiki was recently refreshed. Please wait 7 days to refresh again.