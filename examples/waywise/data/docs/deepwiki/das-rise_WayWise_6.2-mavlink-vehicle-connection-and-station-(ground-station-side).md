# Source: https://deepwiki.com/das-rise/WayWise/6.2-mavlink-vehicle-connection-and-station-(ground-station-side)

The ground-station side of the MAVLink communication layer is responsible for discovering vehicles, managing telemetry pipelines, and providing a high-level API for commanding vehicles. This is achieved through a hierarchy of classes that wrap the MAVSDK library, providing seamless integration with the WayWise core abstractions such as `VehicleState`

and `PosPoint`

.

The `VehicleConnection`

class serves as the generic interface for all vehicle communication protocols. It defines the contract for telemetry retrieval, parameter management, and autopilot control.

`VehicleState`

and `Gimbal`

objects communication/vehicleconnections/vehicleconnection.h108-111`requestArm()`

, `requestTakeoff()`

, and `setRoute()`

communication/vehicleconnections/vehicleconnection.h41-84If a local `WaypointFollower`

is set via `setWaypointFollowerConnectionLocal()`

, the `VehicleConnection`

redirects commands (start, stop, pause, clearRoute) to the local instance instead of sending MAVLink commands to the physical vehicle communication/vehicleconnections/vehicleconnection.cpp25-87

**Sources:**

`MavsdkStation`

acts as the primary listener for MAVLink traffic. It manages the lifecycle of `MavsdkVehicleConnection`

instances and handles global data distribution like RTCM corrections.

`mavsdk::Mavsdk::subscribe_on_new_system`

to detect new hardware communication/mavsdkstation.cpp18`HEARTBEAT`

message using `mavsdk::MavlinkPassthrough`

to determine the `MAV_TYPE`

before instantiating the connection communication/mavsdkstation.cpp107-126`forwardRtcmData()`

communication/mavsdkstation.cpp48-53The station can listen on multiple interfaces simultaneously:

| Method | Description |
|---|---|
`startListeningUDP(port)` | Opens a UDP listener (default 14540) communication/mavsdkstation.cpp23-34 |
`startListeningSerial(portInfo, baudrate)` | Opens a serial connection for telemetry radios communication/mavsdkstation.cpp36-46 |

**Sources:**

`MavsdkVehicleConnection`

implements the `VehicleConnection`

interface specifically for MAVSDK. It maps MAVSDK plugins (Telemetry, Action, Param, etc.) to WayWise internal states.

The class subscribes to various MAVSDK telemetry streams and updates the `mVehicleState`

object:

`subscribe_position_velocity_ned`

to maintain local ENU consistency communication/vehicleconnections/mavsdkvehicleconnection.cpp107-115 For others, it uses global LLH converted to ENU communication/vehicleconnections/mavsdkvehicleconnection.cpp117-127`coordinateTransforms::yawNEDtoENU`

communication/vehicleconnections/mavsdkvehicleconnection.cpp129-135`updatedBatteryState`

signals communication/vehicleconnections/mavsdkvehicleconnection.cpp86-88During construction, the class determines the specific `VehicleState`

subclass to instantiate based on the MAVLink `MAV_TYPE`

and custom parameters:

`CopterState`

communication/vehicleconnections/mavsdkvehicleconnection.cpp19-22`VEH_WW_OBJ_TYPE`

.
`WAYWISE_OBJECT_TYPE_TRUCK`

, it creates `TruckState`

communication/vehicleconnections/mavsdkvehicleconnection.cpp48-56`CarState`

communication/vehicleconnections/mavsdkvehicleconnection.cpp57-65The class provides a bridge to the `mavsdk::Param`

plugin, allowing synchronous and asynchronous parameter access. It maps MAVSDK results to the internal `VehicleConnection::Result`

enum communication/vehicleconnections/mavsdkvehicleconnection.cpp1102-1122

**Sources:**

This diagram illustrates how a physical vehicle is discovered and mapped to a code-level `VehicleState`

.

**Sources:**

This diagram shows the flow of data from MAVSDK plugins into the WayWise coordinate system.

**Sources:**

| Class | Responsibility | Key Methods |
|---|---|---|
`MavsdkStation` | Network discovery and connection lifecycle. | `startListeningUDP()` , `handleNewMavsdkSystem()` |
`MavsdkVehicleConnection` | Protocol-specific implementation of commands. | `requestArm()` , `setIntParameterOnVehicle()` |
`VehicleConnection` | Interface for UI and Autopilot modules. | `setWaypointFollowerConnectionLocal()` , `getVehicleState()` |
`MavsdkGimbal` | Control for MAVLink-attached gimbals. | `setPitchAndYaw()` , `setMode()` |

**Sources:**

Refresh this wiki

This wiki was recently refreshed. Please wait 7 days to refresh again.