# Source: https://deepwiki.com/das-rise/WayWise/6.1-mavlink-vehicle-server-(on-vehicle-side)

The `MavsdkVehicleServer`

is the primary communication gateway residing on the vehicle. It implements the MAVLink protocol using the MAVSDK library to expose the vehicle's state, telemetry, and control interfaces to ground stations (such as `MavsdkStation`

) or other MAVLink-compatible software (e.g., QGroundControl). It acts as a bridge between the internal WayWise abstractions (like `VehicleState`

and `WaypointFollower`

) and the standardized MAVLink messaging system.

`MavsdkVehicleServer`

inherits from the `VehicleServer`

abstract base class communication/vehicleserver.h19-23 This base class defines the mandatory interface for any vehicle-side server, including setters for hardware and software components like `UbloxRover`

, `MovementController`

, and `WaypointFollower`

communication/vehicleserver.h24-32 It also establishes a set of common signals used to trigger autopilot actions based on incoming network commands communication/vehicleserver.h34-44

The server initializes a MAVSDK instance configured as an `Autopilot`

component type communication/mavsdkvehicleserver.cpp22-25 It assigns a unique System ID derived from the `VehicleState`

communication/mavsdkvehicleserver.cpp20-24

Key server plugins are instantiated to handle different MAVLink dialects:

**Sources:** communication/mavsdkvehicleserver.cpp15-41 communication/vehicleserver.h19-61

The server uses a `QTimer`

(`mPublishMavlinkTimer`

) to stream telemetry data at a regular interval (typically 10Hz) communication/mavsdkvehicleserver.cpp48

`mVehicleState`

using `PosType::fused`

. Local ENU coordinates are converted to Global LLH (Latitude, Longitude, Height) using `coordinateTransforms::enuToLlh`

before transmission communication/mavsdkvehicleserver.cpp49-72`ubx_nav_pvt`

data is mapped to `mavsdk::TelemetryServer::RawGps`

structures communication/mavsdkvehicleserver.cpp39-40 communication/mavsdkvehicleserver.cpp77**Sources:** communication/mavsdkvehicleserver.cpp48-78 communication/mavsdkvehicleserver.h48-53

The `ActionServer`

and `MissionRawServer`

plugins map MAVLink commands to WayWise autopilot signals.

The server allows specific flight modes: `Mission`

(Waypoint following) and `Offboard`

(Follow Point/Remote Control) communication/mavsdkvehicleserver.cpp43-45 When a mode change is requested via MAVLink:

`startWaypointFollower`

communication/mavsdkvehicleserver.cpp86`startFollowPoint`

communication/mavsdkvehicleserver.cpp89Incoming MAVLink missions are intercepted via `subscribe_incoming_mission`

communication/mavsdkvehicleserver.cpp105

`PosPoint`

objects using `convertMissionItemToPosPoint`

communication/mavsdkvehicleserver.cpp112-114`WaypointFollower`

via `addRoute()`

communication/mavsdkvehicleserver.cpp116**Sources:** communication/mavsdkvehicleserver.cpp80-121 autopilot/purepursuitwaypointfollower.cpp88-116

The `MavlinkPassthrough`

plugin is used for low-level MAVLink message handling that falls outside standard MAVSDK plugins.

`MAVLINK_MSG_ID_MANUAL_CONTROL`

. It extracts x/y axis data and maps them to speed and steering commands for the `MovementController`

communication/mavsdkvehicleserver.cpp66`UbloxRover`

via the `rxRtcmData`

signal communication/vehicleserver.h43`TRLR_YAW`

(articulation angle), using a custom system ID communication/mavsdkvehicleserver.h70**Sources:** communication/mavsdkvehicleserver.cpp66 communication/mavsdkvehicleserver.h52-55 communication/vehicleserver.h43

To ensure safety during remote operations, the `VehicleServer`

implements a watchdog mechanism.

`heartbeatReset()`

is called, which restarts `mHeartbeatTimer`

communication/mavsdkvehicleserver.cpp142`mCountdown_ms`

(default 2000ms), `heartbeatTimeout()`

triggers communication/mavsdkvehicleserver.cpp141 This usually results in an emergency stop or a transition to a safe state.**Sources:** communication/mavsdkvehicleserver.cpp138-142 communication/vehicleserver.h53-58

This diagram illustrates how MAVSDK Server plugins bridge MAVLink messages to WayWise C++ classes and signals.

**Sources:** communication/mavsdkvehicleserver.cpp33-121 communication/vehicleserver.h34-44

This diagram shows the sequence of the 10Hz telemetry update managed by `mPublishMavlinkTimer`

.

Refresh this wiki

This wiki was recently refreshed. Please wait 7 days to refresh again.