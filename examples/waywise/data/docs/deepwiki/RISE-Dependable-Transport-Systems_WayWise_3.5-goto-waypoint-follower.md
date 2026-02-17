# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/3.5-goto-waypoint-follower

The `GotoWaypointFollower`

provides a high-level waypoint navigation implementation primarily designed for PX4-based drones and other aerial vehicles. It executes waypoint sequences by issuing individual goto commands through the `VehicleConnection`

interface, with proximity-based waypoint advancement. Unlike pure pursuit or other continuous path-following algorithms, this implementation operates at the flight controller level by delegating navigation commands directly to the autopilot system.

The system is designed for scenarios requiring sequential waypoint navigation without on-board path tracking. The vehicle's own autopilot (typically PX4) handles the low-level trajectory planning between waypoints.

For advanced path tracking with lookahead algorithms, see Pure Pursuit Implementation. For dynamic target following, see Follow Point Controller. For the abstract interface specification, see Waypoint Follower Interface.

The `GotoWaypointFollower`

class implements the `WaypointFollower`

abstract interface and operates as a finite state machine that manages sequential waypoint execution. It delegates actual navigation to the vehicle's autopilot by issuing high-level goto commands through the `VehicleConnection::requestGotoENU()`

method.

**Sources:** autopilot/gotowaypointfollower.h28-68 autopilot/gotowaypointfollower.cpp8-13 userinterface/flyui.cpp137-158

The `GotoWaypointFollower`

operates using a finite state machine defined by the `GotoWayPointFollowerSTMstates`

enumeration. The state machine is driven by the `updateState()`

method, which is invoked by `mUpdateStateTimer`

every 200ms. The state machine handles waypoint sequence execution with configurable hold periods between waypoints.

The state machine implementation is located in `updateState()`

, which is triggered by the timer every `mUpdateStatePeriod_ms`

(200ms). The hold position state uses `mUpdateWaypointPeriod_ms`

(5000ms) to pause at each waypoint before advancing.

**Sources:** autopilot/gotowaypointfollower.h16 autopilot/gotowaypointfollower.cpp109-172

The state management is centralized in the `GotoWayPointFollowerState`

struct, which tracks the current navigation state and parameters:

| Field | Type | Default | Description |
|---|---|---|---|
`stmState` | `GotoWayPointFollowerSTMstates` | `NONE` | Current state machine state |
`currentGoal` | `PosPoint` | - | Active waypoint target |
`currentWaypointIndex` | `int` | - | Index in waypoint list |
`waypointProximity` | `double` | 3.0 m | Arrival detection threshold |
`repeatRoute` | `bool` | `false` | Enable route repetition |
`overrideAltitude` | `double` | 0.0 m | Fixed altitude for aerial vehicles |

**Sources:** autopilot/gotowaypointfollower.h17-26

The implementation uses a `QTimer`

with a default 200ms update period to drive the state machine. Key timing parameters include:

`mUpdateStatePeriod_ms`

: 200ms - State machine update frequency`mUpdateWaypointPeriod_ms`

: 5000ms - Hold time at each waypoint`mUpdateStateSumator`

: Accumulator for hold period timing**Sources:** autopilot/gotowaypointfollower.h60-63 autopilot/gotowaypointfollower.cpp11

The waypoint following logic operates through several key methods that implement the navigation behavior. The primary command interface is `VehicleConnection::requestGotoENU()`

, which sends goto commands in the ENU (East-North-Up) coordinate frame.

The `getCurrentVehiclePosition()`

method retrieves the vehicle's position from `VehicleState`

using the configured `mPosTypeUsed`

(default: `PosType::fused`

). The distance check uses the 3D Euclidean distance calculation via `PosPoint::getDistanceTo3d()`

.

**Sources:** autopilot/gotowaypointfollower.cpp35-43 autopilot/gotowaypointfollower.cpp99-107 autopilot/gotowaypointfollower.cpp129-140

The `FlyUI`

component creates and manages `GotoWaypointFollower`

instances for drone route execution. The integration occurs through the `gotRouteForAutopilot()`

slot, which performs safety checks before creating the follower.

The safety check ensures all waypoints remain within `mLineOfSightDistance`

(default 200m) from the home position. If any waypoint exceeds this distance, the entire route is discarded with a debug warning.

**Sources:** userinterface/flyui.cpp137-158 userinterface/flyui.h89

For aerial vehicles, the `GotoWaypointFollower`

implements an altitude override mechanism that maintains a constant flight height regardless of waypoint altitude specifications. This prevents unintended altitude changes during route execution, which is a critical safety feature for drone operations.

The override is applied in two places:

`currentGoal`

in the `FOLLOW_ROUTE_INIT`

state`FOLLOW_ROUTE_HOLD_POSITION`

stateA debug message is logged at the start to inform users that route altitude data is being ignored.

**Sources:** autopilot/gotowaypointfollower.cpp47-48 autopilot/gotowaypointfollower.cpp120-121 autopilot/gotowaypointfollower.cpp149-150

The GotoWaypointFollower provides several configuration options accessible through public methods:

| Method | Parameter | Purpose |
|---|---|---|
`setWaypointProximity()` | `double` meters | Distance threshold for waypoint arrival |
`setRepeatRoute()` | `bool` | Enable automatic route repetition |
`setPosTypeUsed()` | `PosType` | Position source (GNSS, fused, etc.) |

The system supports different position types through the PosType enumeration, allowing selection of position sources based on accuracy requirements and sensor availability.

**Sources:** autopilot/gotowaypointfollower.cpp84-97 autopilot/gotowaypointfollower.h49-53

Refresh this wiki
