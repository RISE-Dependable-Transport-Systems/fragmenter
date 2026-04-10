# Source: https://deepwiki.com/das-rise/WayWise/5-autopilot-and-route-following

The Autopilot subsystem in WayWise is responsible for translating high-level route information into actionable steering and speed commands. It utilizes a modular architecture centered around the `WaypointFollower`

interface, allowing different algorithms (such as Pure Pursuit or dynamic point following) to be swapped or combined depending on the vehicle type and mission requirements.

All autopilot implementations derive from the `WaypointFollower`

abstract base class. This interface establishes a common API for managing routes, controlling execution state, and signaling safety events.

| Method | Description |
|---|---|
`addRoute(const QList<PosPoint>& route)` | Ingests a list of waypoints for the vehicle to follow. |
`startFollowingRoute(bool fromBeginning)` | Transitions the internal state machine to an active following state. |
`stop()` | Halts the current following operation. |
`getCurrentGoal()` | Returns the immediate target `PosPoint` the follower is aiming for. |
`isActive()` | Boolean check for whether the autopilot is currently controlling the vehicle. |

**Signals & Safety:**
The interface includes critical safety signals `activateEmergencyBrake()`

and `deactivateEmergencyBrake()`

. These are typically connected to the `EmergencyBrake`

class to enable or disable automated safety interventions during autonomous operation.

**Sources:** autopilot/waypointfollower.h14-38

WayWise provides several specialized followers to handle different navigation scenarios:

The `EmergencyBrake`

class serves as a safety interlock between sensors and the movement controllers. It maintains an `EmergencyBrakeState`

that tracks detections from various sources (Camera, LiDAR, Radar).

**Logic Flow:**

`emergencyBrakeIsActive`

is true (typically signaled by the active `WaypointFollower`

).`brakeForDetectedCameraObject(const PosPoint &detectedObject)`

.`fuseSensorsAndTakeBrakeDecision()`

function evaluates if any detected object is within the `brakeForObjectAtDistance`

threshold (default 10m).`emergencyBrake()`

signal, which is intercepted by the `MovementController`

to zero out velocity.For details, see Emergency Brake.

**Sources:** autopilot/emergencybrake.h15-40 autopilot/emergencybrake.cpp23-43

The following diagram illustrates how the abstract autopilot concepts map to specific classes and data structures within the WayWise codebase.

**Autopilot Entity Mapping**

**Sources:** autopilot/waypointfollower.h14-38 autopilot/emergencybrake.h15-22

Most autopilot implementations in WayWise follow a State Machine (STM) pattern to manage transitions between idling, following, and reaching the end of a route. These state machines are typically updated in a high-frequency loop (e.g., every 50ms) to ensure responsive steering.

**Autopilot Control Flow**

**Sources:** autopilot/waypointfollower.h35-37 autopilot/emergencybrake.cpp36-43

Refresh this wiki

This wiki was recently refreshed. Please wait 7 days to refresh again.