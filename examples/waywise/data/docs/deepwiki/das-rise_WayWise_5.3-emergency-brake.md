# Source: https://deepwiki.com/das-rise/WayWise/5.3-emergency-brake

The `EmergencyBrake`

class serves as a safety interlock layer within the WayWise autopilot system. It is responsible for monitoring sensor inputs (such as depth cameras) and enforcing a stop command if obstacles are detected while the autopilot is active. It operates on a signal/slot pattern, allowing it to be enabled or disabled by various `WaypointFollower`

implementations to ensure safety during autonomous missions while avoiding interference during manual operation.

The `EmergencyBrake`

class maintains an internal state via the `EmergencyBrakeState`

struct, which tracks whether the brake is globally active and whether specific sensors have triggered a stop condition autopilot/emergencybrake.h15-21

The core decision logic is encapsulated in `fuseSensorsAndTakeBrakeDecision()`

. This function evaluates the current sensor flags and, if the emergency brake system is enabled, emits the `emergencyBrake()`

signal to stop the vehicle autopilot/emergencybrake.cpp36-43

Currently, the system primarily integrates with camera-based object detection:

`PosPoint`

is received from a camera (typically representing the closest detected object), the system calculates the Euclidean distance from the vehicle autopilot/emergencybrake.cpp25-26`brakeForObjectAtDistance`

(default 10 meters), the `brakeForDetectedCameraObject`

flag is set to true autopilot/emergencybrake.cpp28-31The following diagram illustrates how the `EmergencyBrake`

class bridges sensor data to vehicle stop commands.

**Emergency Brake Data Flow**

Sources: autopilot/emergencybrake.cpp23-43 autopilot/emergencybrake.h15-21

The emergency brake system follows a "safety-on-by-default" or "context-aware" activation pattern. It is controlled by the `WaypointFollower`

(or its derivatives like `FollowPoint`

) via signals.

`activateEmergencyBrake()`

. For example, if `FollowPoint`

loses its target heartbeat, it stops the vehicle and activates the emergency brake interlock autopilot/followpoint.cpp74-82`deactivateEmergencyBrake()`

to allow the movement controller to follow the generated trajectory without being immediately tripped by the safety logic (unless a new obstacle appears) autopilot/followpoint.cpp65-67**Waypoint Follower Interlock Control**

Sources: autopilot/followpoint.cpp65-82 autopilot/waypointfollower.h35-38 autopilot/emergencybrake.cpp13-21

While the `EmergencyBrake`

class evaluates the logic, the actual stopping of the vehicle is performed by the `MovementController`

. The `emergencyBrake()`

signal is typically connected to the movement controller's stop or speed-override functions.

In the `FollowPoint`

implementation, if the system is not actively following, it calls `holdPosition()`

, which explicitly sets the `MovementController`

desired steering and speed to 0.0 autopilot/followpoint.cpp84-92 The `EmergencyBrake`

acts as a redundant safety layer that can trigger this stop independently of the waypoint following logic if an obstacle is detected autopilot/emergencybrake.cpp41

The `EmergencyBrakeState`

struct defines the following internal parameters:

| Parameter | Type | Default | Description |
|---|---|---|---|
`brakeForObjectAtDistance` | `double` | 10.0 | Distance in meters at which a detected object triggers a brake condition autopilot/emergencybrake.h19 |
`emergencyBrakeIsActive` | `bool` | `false` | Global enable/disable flag for the safety logic autopilot/emergencybrake.h20 |
`brakeForDetectedCameraObject` | `bool` | `false` | Internal flag set when a camera object is within the threshold autopilot/emergencybrake.h16 |

Sources: autopilot/emergencybrake.h15-21

Refresh this wiki

This wiki was recently refreshed. Please wait 7 days to refresh again.