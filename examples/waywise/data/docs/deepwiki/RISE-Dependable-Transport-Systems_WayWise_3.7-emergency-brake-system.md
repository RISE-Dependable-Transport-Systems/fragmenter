# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/3.7-emergency-brake-system

The Emergency Brake System provides a safety layer that processes sensor inputs (camera, lidar, radar) to make braking decisions. It acts as an interrupt mechanism that can halt vehicle motion when obstacles are detected within a configured distance threshold. The system is designed to be activated by autopilot components and to emit brake commands based on sensor fusion logic.

For information about autopilot components that control the emergency brake activation, see Waypoint Follower Interface. For sensor integration details, see Sensor Integration.

The Emergency Brake System consists of two primary components: the `EmergencyBrake`

class that implements the decision logic, and the `EmergencyBrakeState`

structure that maintains the current sensor readings and configuration.

**Diagram: Emergency Brake System Architecture**

The system integrates with autopilot components through Qt signal-slot connections. Autopilot implementations (derived from `WaypointFollower`

) emit activation signals to enable the emergency brake, while sensor detection modules call slots on `EmergencyBrake`

to report detected obstacles.

**Sources:** autopilot/emergencybrake.h1-42 autopilot/waypointfollower.h14-38

The `EmergencyBrakeState`

structure maintains the current state of all sensor inputs and configuration parameters.

| Field | Type | Default | Description |
|---|---|---|---|
`brakeForDetectedCameraObject` | `bool` | `false` | Flag indicating camera detected an obstacle within threshold |
`brakeForDetectedLidarObject` | `bool` | `false` | Flag indicating lidar detected an obstacle (future) |
`brakeForDetectedRadarObject` | `bool` | `false` | Flag indicating radar detected an obstacle (future) |
`brakeForObjectAtDistance` | `double` | `10.0` | Distance threshold in meters for triggering brake |
`emergencyBrakeIsActive` | `bool` | `false` | Master enable flag controlled by autopilot |

The structure is defined in autopilot/emergencybrake.h15-21 and serves as a centralized state store for all sensor-based brake conditions. The `emergencyBrakeIsActive`

flag acts as a master switch: when `false`

, no brake commands are emitted regardless of sensor inputs.

**Sources:** autopilot/emergencybrake.h15-21

The `EmergencyBrake`

class implements the sensor fusion and decision logic. It inherits from `QObject`

to support Qt's signal-slot mechanism.

**Diagram: EmergencyBrake Class Structure**

**Sources:** autopilot/emergencybrake.h23-42 autopilot/emergencybrake.cpp1-44

Enables the emergency brake system by setting `mCurrentState.emergencyBrakeIsActive = true`

. This method is typically connected to the `WaypointFollower::activateEmergencyBrake()`

signal, allowing autopilot components to enable safety monitoring when starting autonomous operation.

Implementation: autopilot/emergencybrake.cpp18-21

Disables the emergency brake system by setting `mCurrentState.emergencyBrakeIsActive = false`

. This prevents brake commands from being emitted, effectively putting the system in a dormant state. Connected to `WaypointFollower::deactivateEmergencyBrake()`

signal for disabling when autopilot stops.

Implementation: autopilot/emergencybrake.cpp13-16

Processes camera-based object detection. The method calculates the Euclidean distance to the detected object:

```
distance = sqrt(x² + y² + height²)
```


If the distance is greater than zero and less than `mCurrentState.brakeForObjectAtDistance`

(default 10m), the `brakeForDetectedCameraObject`

flag is set to `true`

. Otherwise, it is set to `false`

. After updating the flag, `fuseSensorsAndTakeBrakeDecision()`

is called to evaluate whether to emit a brake command.

**Note:** When no object is detected, the input `PosPoint`

should have zero coordinates, resulting in a distance of zero and preventing false brake activation.

Implementation: autopilot/emergencybrake.cpp23-34

**Sources:** autopilot/emergencybrake.cpp23-34

This method implements the sensor fusion and decision logic. It performs two checks:

`mCurrentState.emergencyBrakeIsActive == true`

(master enable)`brakeForDetectedCameraObject`

)If both conditions are met, the method emits the `emergencyBrake()`

signal. The current implementation has a placeholder comment indicating future expansion: "ToDo: create decission logic depending on multiple sensor inputs" autopilot/emergencybrake.cpp39

**Diagram: Sensor Fusion Decision Flow**

Implementation: autopilot/emergencybrake.cpp36-43

**Sources:** autopilot/emergencybrake.cpp36-43

Emitted when the system determines that an emergency brake should be applied. This signal should be connected to vehicle control components (such as `VehicleConnection`

or `MovementController`

) to immediately halt vehicle motion. The signal carries no parameters; the receiving component is responsible for implementing the appropriate brake behavior (e.g., setting throttle to zero, engaging physical brakes).

Declaration: autopilot/emergencybrake.h30

**Sources:** autopilot/emergencybrake.h30

The `WaypointFollower`

abstract interface defines two signals that integrate with the emergency brake system:

**Diagram: Emergency Brake Activation Sequence**

The `WaypointFollower::activateEmergencyBrake()`

and `WaypointFollower::deactivateEmergencyBrake()`

signals are defined in autopilot/waypointfollower.h36-37 These signals should be emitted by concrete implementations (such as `PurepursuitWaypointFollower`

) when starting and stopping route following, respectively.

**Connection Setup Example:**

**Sources:** autopilot/waypointfollower.h36-37 autopilot/emergencybrake.cpp13-21

The current implementation processes camera-based object detection. Future expansion is planned for lidar and radar inputs.

**Diagram: Camera Object Detection Processing Flow**

**Distance Calculation:**

The distance is calculated using 3D Euclidean distance autopilot/emergencybrake.cpp26:

```
objectDistance = sqrt(detectedObject.x² + detectedObject.y² + detectedObject.height²)
```


When `objectDistance`

is zero (no object detected), the brake flag remains `false`

. When `objectDistance`

is non-zero and less than the threshold (default 10m), the brake flag is set to `true`

.

**Sources:** autopilot/emergencybrake.cpp23-34

The emergency brake system has a basic implementation that supports camera-based object detection. The code includes placeholders for future sensor integration:

| Sensor Type | Status | State Field |
|---|---|---|
| Camera | Implemented | `brakeForDetectedCameraObject` |
| Lidar | Planned | `brakeForDetectedLidarObject` |
| Radar | Planned | `brakeForDetectedRadarObject` |

The `EmergencyBrakeState`

structure includes fields for lidar and radar autopilot/emergencybrake.h17-18 but no corresponding slot methods exist yet to process these inputs. The `fuseSensorsAndTakeBrakeDecision()`

method contains a TODO comment autopilot/emergencybrake.cpp39 indicating that more sophisticated decision logic is planned to combine multiple sensor types.

**Future Enhancements:**

`brakeForDetectedLidarObject(const PosPoint &)`

slot to process point cloud data`brakeForDetectedRadarObject(const PosPoint &)`

slot for radar-based detection`brakeForObjectAtDistance`

value**Sources:** autopilot/emergencybrake.h15-21 autopilot/emergencybrake.cpp36-43

The emergency brake system currently has one configurable parameter stored in `EmergencyBrakeState`

:

`double`

`10.0`

meters**Access:** The parameter is currently private within `mCurrentState`

. To make it runtime-configurable, the `EmergencyBrake`

class would need to provide getter/setter methods or integrate with the `ParameterServer`

system (see Parameter Server).

**Sources:** autopilot/emergencybrake.h19

The following demonstrates typical usage of the emergency brake system in an autopilot application:

**Sources:** autopilot/emergencybrake.h1-42 autopilot/emergencybrake.cpp1-44 autopilot/waypointfollower.h14-38

Refresh this wiki
