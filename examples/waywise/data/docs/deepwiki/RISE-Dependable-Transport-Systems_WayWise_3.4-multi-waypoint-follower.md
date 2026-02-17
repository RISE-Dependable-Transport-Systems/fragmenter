# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/3.4-multi-waypoint-follower

The `MultiWaypointFollower`

class manages multiple `WaypointFollower`

instances and enables runtime switching between them. It implements the delegation pattern, forwarding all `WaypointFollower`

interface methods to the currently active follower selected by `mActiveWaypointFollowerID`

.

For information about the base interface, see page 3.1. For specific implementations, see pages 3.2 (Pure Pursuit), 3.3 (Follow Point), and 3.5 (Goto).

Sources: autopilot/multiwaypointfollower.h1-66 autopilot/multiwaypointfollower.cpp1-161

The `MultiWaypointFollower`

stores `WaypointFollower`

instances in `mWaypointFollowerList`

and delegates operations to `mWaypointFollowerList[mActiveWaypointFollowerID]`

. This enables:

`setActiveWaypointFollower()`

`WaypointFollower`

interface regardless of underlying implementation`PurepursuitWaypointFollower`

-specific parametersSources: autopilot/multiwaypointfollower.h5-6 autopilot/multiwaypointfollower.cpp9-15 autopilot/multiwaypointfollower.h60-62

**MultiWaypointFollower Class Structure**

The diagram shows how `MultiWaypointFollower`

inherits from `WaypointFollower`

while also containing multiple `WaypointFollower`

instances. This composition pattern allows it to delegate to any contained follower while presenting the same interface to clients.

Sources: autopilot/multiwaypointfollower.h17-63 autopilot/multiwaypointfollower.h14-15

**Method Delegation Pattern**

All `WaypointFollower`

interface methods forward to `mWaypointFollowerList[mActiveWaypointFollowerID]`

. For example, `addRoute()`

at autopilot/multiwaypointfollower.cpp42-45 delegates to the active follower's `addRoute()`

implementation. `PurepursuitWaypointFollower`

instances have their `distanceOfRouteLeft`

signal connected at autopilot/multiwaypointfollower.cpp11-13 and forwarded via `receiveDistanceOfRouteLeft()`

at autopilot/multiwaypointfollower.cpp152-155

Sources: autopilot/multiwaypointfollower.cpp32-65 autopilot/multiwaypointfollower.cpp152-155 autopilot/multiwaypointfollower.h60-62

Followers are added to the container using `addWaypointFollower()`

:

| Method | Parameters | Returns | Description |
|---|---|---|---|
`addWaypointFollower()` | `QSharedPointer<WaypointFollower>` | `int` | Adds a follower to the list and returns its index |
`getNumberOfWaypointFollowers()` | - | `int` | Returns the total number of contained followers |

The first follower added becomes the initial active follower (index 0). Special handling is performed for `PurepursuitWaypointFollower`

instances - their `distanceOfRouteLeft`

signal is connected to the container's signal forwarder.

Sources: autopilot/multiwaypointfollower.cpp110-118 autopilot/multiwaypointfollower.cpp147-150

Runtime switching between followers is accomplished through:

The `mActiveWaypointFollowerID`

member variable tracks which follower is currently active. All delegated operations use this index to select the target follower from `mWaypointFollowerList`

.

Sources: autopilot/multiwaypointfollower.cpp137-145 autopilot/multiwaypointfollower.h60-62

The constructor requires at least one initial follower:

This follower is added to the list and signal connections are established if it's a `PurepursuitWaypointFollower`

instance.

Sources: autopilot/multiwaypointfollower.cpp9-15 autopilot/multiwaypointfollower.h21

All standard interface methods delegate directly to the active follower:

| Method | Delegation Target | Line Reference |
|---|---|---|
`clearRoute()` | `mWaypointFollowerList[mActiveWaypointFollowerID]->clearRoute()` | 32-35 |
`addWaypoint()` | `mWaypointFollowerList[mActiveWaypointFollowerID]->addWaypoint()` | 37-40 |
`addRoute()` | `mWaypointFollowerList[mActiveWaypointFollowerID]->addRoute()` | 42-45 |
`startFollowingRoute()` | `mWaypointFollowerList[mActiveWaypointFollowerID]->startFollowingRoute()` | 47-50 |
`isActive()` | `mWaypointFollowerList[mActiveWaypointFollowerID]->isActive()` | 52-55 |
`stop()` | `mWaypointFollowerList[mActiveWaypointFollowerID]->stop()` | 57-60 |
`resetState()` | `mWaypointFollowerList[mActiveWaypointFollowerID]->resetState()` | 62-65 |
`getCurrentGoal()` | `mWaypointFollowerList[mActiveWaypointFollowerID]->getCurrentGoal()` | 27-30 |
`getCurrentRoute()` | `mWaypointFollowerList[mActiveWaypointFollowerID]->getCurrentRoute()` | 157-160 |
`getRepeatRoute()` | `mWaypointFollowerList[mActiveWaypointFollowerID]->getRepeatRoute()` | 17-20 |
`setRepeatRoute()` | `mWaypointFollowerList[mActiveWaypointFollowerID]->setRepeatRoute()` | 22-25 |

This delegation is implemented with simple one-line forwarding, ensuring zero overhead beyond the virtual function call.

Sources: autopilot/multiwaypointfollower.cpp17-65 autopilot/multiwaypointfollower.cpp157-160

The `MultiWaypointFollower`

provides special handling for `PurepursuitWaypointFollower`

instances, allowing control over Pure Pursuit-specific parameters even when working through the generic interface.

| Method | Target | Behavior |
|---|---|---|
`getPurePursuitRadius()` | Active follower only | Returns radius if active follower is Pure Pursuit, otherwise 0 |
`setPurePursuitRadius()` | All followers | Sets radius on all Pure Pursuit followers in the list |
`setAdaptivePurePursuitRadiusActive()` | All followers | Enables/disables adaptive radius on all Pure Pursuit followers |
`getAdaptivePurePursuitRadiusCoefficient()` | Active follower only | Returns coefficient if active follower is Pure Pursuit, otherwise 0 |
`setAdaptivePurePursuitRadiusCoefficient()` | All followers | Sets coefficient on all Pure Pursuit followers |

Note the asymmetry: getter methods query only the active follower, while setter methods apply to **all** Pure Pursuit followers in the container. This design ensures consistent parameter values across all Pure Pursuit instances.

Sources: autopilot/multiwaypointfollower.cpp67-108 autopilot/multiwaypointfollower.h38-43

The implementation uses `qSharedPointerDynamicCast<PurepursuitWaypointFollower>()`

at autopilot/multiwaypointfollower.cpp78 to check follower type before calling Pure Pursuit-specific methods. If the cast fails, a debug message is logged. This pattern at autopilot/multiwaypointfollower.cpp75-82 is repeated for `setAdaptivePurePursuitRadiusActive()`

at autopilot/multiwaypointfollower.cpp84-91 and `setAdaptivePurePursuitRadiusCoefficient()`

at autopilot/multiwaypointfollower.cpp101-108 ensuring type safety while allowing heterogeneous follower lists.

Sources: autopilot/multiwaypointfollower.cpp75-82 autopilot/multiwaypointfollower.cpp84-91 autopilot/multiwaypointfollower.cpp101-108

**Signal Forwarding Architecture**

The `distanceOfRouteLeft(double)`

signal from `PurepursuitWaypointFollower`

instances is connected at autopilot/multiwaypointfollower.cpp11-13 during construction and at autopilot/multiwaypointfollower.cpp112-114 when adding new followers. The slot `receiveDistanceOfRouteLeft()`

at autopilot/multiwaypointfollower.cpp152-155 immediately re-emits the signal.

Sources: autopilot/multiwaypointfollower.cpp11-13 autopilot/multiwaypointfollower.cpp112-114 autopilot/multiwaypointfollower.cpp152-155

**Parameter Server Registration Pattern**

The `MultiWaypointFollower`

registers Pure Pursuit parameters with the `ParameterServer`

for remote configuration. Parameters are named using the pattern `PP<ID>_<PARAM>`

where `<ID>`

is the follower index.

Two overloaded methods handle parameter registration:

The parameterless version iterates through all followers and calls the indexed version for each.

Sources: autopilot/multiwaypointfollower.cpp120-135 autopilot/multiwaypointfollower.h50-51

For each follower index, two parameters are registered:

| Parameter Name | Setter | Getter | Description |
|---|---|---|---|
`PP<ID>_RADIUS` | `setPurePursuitRadius()` | `getPurePursuitRadius()` | Pure Pursuit lookahead radius |
`PP<ID>_ARC` | `setAdaptivePurePursuitRadiusCoefficient()` | `getAdaptivePurePursuitRadiusCoefficient()` | Adaptive radius coefficient |

These parameters are accessible through the MAVLink parameter protocol when `ParameterServer`

is active.

Sources: autopilot/multiwaypointfollower.cpp129-134

**Initialization and Configuration**

Construction at autopilot/multiwaypointfollower.cpp9-15 requires an initial follower. Additional followers are added via `addWaypointFollower()`

at autopilot/multiwaypointfollower.cpp110-118 Parameters are registered at autopilot/multiwaypointfollower.cpp120-135 All subsequent method calls delegate to `mWaypointFollowerList[mActiveWaypointFollowerID]`

.

Sources: autopilot/multiwaypointfollower.cpp9-15 autopilot/multiwaypointfollower.cpp110-118 autopilot/multiwaypointfollower.cpp120-135

Switching between navigation strategies:

| Step | Method Calls | Effect |
|---|---|---|
| 1. Start Pure Pursuit | `setActiveWaypointFollower(0)` `addRoute(preciseRoute)` `startFollowingRoute()` | `mActiveWaypointFollowerID = 0` Delegates to `PurepursuitWaypointFollower` |
| 2. Switch to Goto | `stop()` `setActiveWaypointFollower(1)` `addRoute(waypointRoute)` `startFollowingRoute()` | Stops follower [0]`mActiveWaypointFollowerID = 1` Delegates to `GotoWaypointFollower` |
| 3. Return to Pure Pursuit | `stop()` `setActiveWaypointFollower(0)` `startFollowingRoute()` | Stops follower [1]`mActiveWaypointFollowerID = 0` |

The `setActiveWaypointFollower()`

method at autopilot/multiwaypointfollower.cpp137-140 updates `mActiveWaypointFollowerID`

, redirecting all subsequent delegated calls.

Sources: autopilot/multiwaypointfollower.cpp137-145 autopilot/multiwaypointfollower.cpp47-60

| Variable | Type | Description |
|---|---|---|
`mWaypointFollowerList` | `QList<QSharedPointer<WaypointFollower>>` | Container for all follower instances |
`mActiveWaypointFollowerID` | `int` | Index of the currently active follower (default: 0) |

Sources: autopilot/multiwaypointfollower.h60-62

**Shared Pointers**: All followers are stored as `QSharedPointer<WaypointFollower>`

to enable safe lifetime management and polymorphism.

**Active vs All**: Getter methods query only the active follower, while Pure Pursuit setter methods apply to all Pure Pursuit instances. This ensures parameter consistency.

**Type Safety**: Dynamic casting (`qSharedPointerDynamicCast`

) is used to safely check and access Pure Pursuit-specific functionality without breaking the abstraction for other follower types.

**Signal Forwarding**: Pure Pursuit signals are explicitly connected and forwarded, allowing clients to receive progress updates regardless of which follower is active.

Sources: autopilot/multiwaypointfollower.cpp67-155 autopilot/multiwaypointfollower.h17-63

Refresh this wiki
