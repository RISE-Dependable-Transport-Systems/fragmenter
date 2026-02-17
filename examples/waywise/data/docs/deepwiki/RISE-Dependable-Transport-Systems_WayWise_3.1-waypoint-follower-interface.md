# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/3.1-waypoint-follower-interface

This page documents the `WaypointFollower`

abstract interface, which defines the contract that all autopilot implementations in WayWise must satisfy. The interface provides a unified API for route management, execution control, and safety system integration.

For specific autopilot implementations, see:

For emergency brake system details, see Emergency Brake System.

**Sources:** autopilot/waypointfollower.h1-40

`WaypointFollower`

is an abstract base class that extends `QObject`

, enabling Qt signal-slot communication for integration with the safety system. All autopilot implementations inherit from this interface and implement its pure virtual methods.

The interface provides three functional areas:

**Class Diagram: WaypointFollower Interface Structure**

**Sources:** autopilot/waypointfollower.h8-40 autopilot/emergencybrake.h8-42

All methods in the `WaypointFollower`

interface are pure virtual (`= 0`

), requiring concrete implementations in derived classes. The table below summarizes the interface contract:

| Method | Return Type | Description |
|---|---|---|
`getRepeatRoute()` | `bool` | Returns whether route repetition is enabled |
`setRepeatRoute(bool)` | `void` | Enables or disables automatic route repetition |
`getCurrentGoal()` | `PosPoint` | Returns the current target waypoint |
`clearRoute()` | `void` | Removes all waypoints from the route |
`addWaypoint(const PosPoint&)` | `void` | Appends a single waypoint to the route |
`addRoute(const QList<PosPoint>&)` | `void` | Appends multiple waypoints to the route |
`startFollowingRoute(bool)` | `void` | Begins route execution; parameter determines if starting from beginning |
`isActive()` | `bool` | Returns `true` if autopilot is currently following a route |
`stop()` | `void` | Halts autopilot execution immediately |
`resetState()` | `void` | Resets internal state machine to initial condition |
`getCurrentRoute()` | `QList<PosPoint>` | Returns the complete list of waypoints in the route |

**Sources:** autopilot/waypointfollower.h19-33

The interface provides three methods for route manipulation:

Removes all waypoints from the current route. Implementations must ensure that calling this method does not affect the autopilot's active state—if the autopilot is running when the route is cleared, behavior is implementation-defined.

Appends a single waypoint to the end of the current route. The `PosPoint`

structure contains position (`x`

, `y`

, `height`

), orientation (`yaw`

), and optional metadata such as speed limits and custom attributes.

Appends multiple waypoints in sequence. This is more efficient than calling `addWaypoint()`

repeatedly for large routes. Implementations may optimize batch additions.

**Route Building Example Flow**

**Sources:** autopilot/waypointfollower.h24-26

The interface defines methods for controlling autopilot lifecycle:

Initiates route following. The boolean parameter controls initialization behavior:

`true`

: Start from the first waypoint, regardless of previous state`false`

: Resume from the last known position in the route (if applicable)Implementations typically transition from an idle state to an active state machine when this method is called.

Returns `true`

if the autopilot is currently executing a route. This is used by UI components and safety systems to determine operational status.

Immediately halts route following. Implementations must ensure that vehicle control commands cease and the autopilot enters an idle state. The current route remains in memory and can be resumed.

Resets the internal state machine to its initial condition. This typically includes:

Unlike `stop()`

, this method is typically called when preparing for a new route or after an error condition.

Controls whether the autopilot should automatically restart from the beginning when reaching the final waypoint. This is useful for patrol patterns or continuous testing.

**Autopilot Lifecycle State Machine**

**Sources:** autopilot/waypointfollower.h28-31

Returns the current target waypoint as a `PosPoint`

. Implementations use this to expose the autopilot's immediate objective, enabling visualization on maps and logging systems. The returned point typically includes:

`x`

, `y`

, `height`

)`yaw`

)If no route is active, behavior is implementation-defined (may return an invalid/zero point).

Returns the complete list of waypoints currently stored in the autopilot. This enables:

`MapWidget`

The returned list should match the order in which waypoints were added via `addWaypoint()`

or `addRoute()`

.

**Sources:** autopilot/waypointfollower.h22-33

The `WaypointFollower`

interface defines two signals for bidirectional communication with the `EmergencyBrake`

safety system:

Emitted by waypoint follower implementations when they want to disable emergency braking functionality. This typically occurs when:

Emitted when the autopilot wants to enable emergency braking. This typically occurs when:

The `EmergencyBrake`

class provides corresponding slots that respond to these signals. The emergency brake system maintains an `EmergencyBrakeState`

structure with flags for different sensor inputs (camera, lidar, radar) and can trigger an `emergencyBrake()`

signal when an obstacle is detected within the configured distance threshold.

**Signal-Slot Connection Diagram**

**Connection Code Pattern**

When the emergency brake system detects an obstacle (via `brakeForDetectedCameraObject()`

or similar methods), it evaluates the sensor data against the configured threshold distance (autopilot/emergencybrake.cpp26-29). If conditions warrant braking and `emergencyBrakeIsActive`

is `true`

, the system emits the `emergencyBrake()`

signal, which autopilot implementations must handle by stopping the vehicle.

**Sources:** autopilot/waypointfollower.h35-37 autopilot/emergencybrake.h15-21 autopilot/emergencybrake.cpp13-43

Classes implementing the `WaypointFollower`

interface must adhere to the following requirements:

All methods may be called from the Qt main thread or from worker threads. Implementations should use appropriate Qt thread-safe mechanisms (signals/slots, `QMutex`

, etc.) to protect shared state.

`addWaypoint()`

or `addRoute()`

must persist until explicitly cleared with `clearRoute()`

or until the object is destroyed`stop()`

must not clear the route`resetState()`

should not clear the route (resets execution state only)Waypoints provided as `PosPoint`

objects use the ENU (East-North-Up) coordinate system relative to the vehicle's ENU reference origin. Implementations must handle coordinate transformations if the vehicle state uses different coordinate systems internally.

See Position Types & PosPoint Structure for details on the `PosPoint`

structure and coordinate systems.

Implementations typically use internal state machines (e.g., `INIT`

, `FOLLOWING`

, `FINISHED`

in `PurepursuitWaypointFollower`

). The interface methods map to state transitions:

`startFollowingRoute()`

→ Enter active state`stop()`

→ Enter idle/stopped state`isActive()`

→ Query current state category`getCurrentGoal()`

must return a valid `PosPoint`

if `isActive()`

is `true`

`getCurrentRoute()`

should return an empty list if no route has been added`getRepeatRoute()`

should return the last value set by `setRepeatRoute()`

, defaulting to `false`

**Implementation Checklist**

| Requirement | Description |
|---|---|
✓ Inherit from `WaypointFollower` | Use public inheritance |
| ✓ Implement all pure virtual methods | All 11 methods must be implemented |
✓ Emit `activateEmergencyBrake()` | On route start or autonomous mode entry |
✓ Emit `deactivateEmergencyBrake()` | On stop or manual mode entry |
✓ Connect to `EmergencyBrake::emergencyBrake()` | Handle emergency stop signal |
✓ Handle `PosPoint` ENU coordinates | Transform if necessary for vehicle frame |
| ✓ Maintain route persistence | Routes survive `stop()` and `resetState()` |
| ✓ Thread-safe state access | Use Qt mechanisms or mutexes |

**Sources:** autopilot/waypointfollower.h8-40

Waypoint follower implementations operate on `VehicleState`

objects to determine the current vehicle position, velocity, and steering capabilities. The interface itself does not directly reference `VehicleState`

, but concrete implementations typically:

`VehicleState::getPosition()`

to obtain current position in ENU coordinates`MovementController`

or `MavsdkVehicleConnection`

For ground vehicles, implementations use `CarState::getCurvatureToPointInVehicleFrame()`

and related methods. For multicopters, the `CopterState`

specialization provides altitude and velocity control. Articulated vehicles (trucks with trailers) use `TruckState::getCurvatureWithTrailer()`

for trailer-aware path following.

See Vehicle State Management for details on the state hierarchy.

**Sources:** autopilot/waypointfollower.h1-40 vehicles/copterstate.h16-49

Refresh this wiki
