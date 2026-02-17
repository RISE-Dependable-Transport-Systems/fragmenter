# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/2.1-vehicle-server-(mavsdkvehicleserver)

`MavsdkVehicleServer`

provides the vehicle-side MAVLink interface for WayWise autonomous vehicles. It acts as a MAVLink autopilot component, enabling ground stations (e.g., QGroundControl, WayWise Ground Station) to communicate with and control the vehicle. The server publishes telemetry data, accepts mission uploads, handles flight mode changes, processes manual control inputs, and manages RTCM correction data for RTK positioning.

For ground-station-side MAVLink communication, see Vehicle Connection (MavsdkVehicleConnection). For the vehicle discovery and connection management layer, see Ground Station (MavsdkStation).

**Sources:** communication/mavsdkvehicleserver.h1-73 communication/mavsdkvehicleserver.cpp1-30

`MavsdkVehicleServer`

inherits from the abstract `VehicleServer`

base class and integrates with multiple vehicle subsystems. It serves as the central communication hub on the vehicle side, translating between MAVLink protocol messages and internal WayWise components.

**Sources:** communication/mavsdkvehicleserver.cpp15-479 communication/vehicleserver.h19-61

The server initializes MAVSDK with an autopilot component type and configures it to always send heartbeats. The system ID is obtained from the `VehicleState`

object, enabling multi-vehicle support.

| Step | Action | Code Reference |
|---|---|---|
| 1 | Create MAVSDK instance with `ComponentType::Autopilot` | mavsdkvehicleserver.cpp22-25 |
| 2 | Configure system ID from `VehicleState::getId()` | mavsdkvehicleserver.cpp20-24 |
| 3 | Enable heartbeat broadcasting | mavsdkvehicleserver.cpp23 |
| 4 | Retrieve server component | mavsdkvehicleserver.cpp33 |
| 5 | Initialize server plugins (Telemetry, Action, Mission, Parameter) | mavsdkvehicleserver.cpp36-40 |
| 6 | Configure allowable flight modes and arming | mavsdkvehicleserver.cpp43-45 |
| 7 | Setup UDP connection to control tower | mavsdkvehicleserver.cpp463-478 |

**Sources:** communication/mavsdkvehicleserver.cpp15-479

`MavsdkVehicleServer`

integrates four primary MAVSDK server plugins, each handling a specific aspect of the MAVLink protocol:

Publishes vehicle state information to ground stations at 10 Hz (100ms intervals).

**Published Messages:**

`POSITION_VELOCITY_NED`

- Position and velocity in NED frame`GLOBAL_POSITION_INT`

- Global position in LLH`HOME_POSITION`

- Home/origin position`GPS_RAW_INT`

- Raw GNSS data from u-blox receiver`GPS_GLOBAL_ORIGIN`

- ENU reference point**Coordinate Transformations:**

```
VehicleState (ENU) → NED Conversion → TelemetryServer
- X_enu → Y_ned
- Y_enu → X_ned
- Z_enu → -Z_ned
```


**Sources:** communication/mavsdkvehicleserver.cpp48-78 communication/mavsdkvehicleserver.cpp642-663

Handles flight mode changes and arming state.

**Configuration:**

**Flight Mode Mapping:**

| MAVLink Flight Mode | WayWise Action |
|---|---|
`FlightMode::Mission` | Start `WaypointFollower` |
`FlightMode::Offboard` | Start `FollowPoint` |
`FlightMode::Manual` | Stop autopilots |

**Sources:** communication/mavsdkvehicleserver.cpp43-103

Handles mission waypoint uploads from ground stations.

**Subscriptions:**

`subscribe_incoming_mission()`

- Receive complete mission`subscribe_clear_all()`

- Clear all waypoints`subscribe_current_item_changed()`

- Jump to specific waypoint**Mission Item Conversion:**

```
MISSION_ITEM_INT/MISSION_ITEM → PosPoint
- x/y (int32_t, scaled 10e4) → X/Y meters (ENU)
- z (float) → Height meters
- param1 → Speed m/s
- param2 → Attributes bitfield
```


**Sources:** communication/mavsdkvehicleserver.cpp105-136 communication/mavsdkvehicleserver.cpp578-592

Handles custom MAVLink messages not covered by standard plugins.

**Custom Message Handling:**

**Sources:** communication/mavsdkvehicleserver.cpp144-412

Telemetry is published at 100ms intervals via a `QTimer`

. The publishing pipeline performs coordinate transformations and data aggregation before transmission.

**Sources:** communication/mavsdkvehicleserver.cpp48-78 communication/mavsdkvehicleserver.cpp353-411

**ENU to NED Conversion (for telemetry):**

```
Position: [X_enu, Y_enu, Z_enu] → [Y_enu, X_enu, -Z_enu]
Velocity: [Vx_enu, Vy_enu, Vz_enu] → [Vy_enu, Vx_enu, -Vz_enu]
Heading: yaw_enu → coordinateTransforms::yawENUtoNED(yaw_enu)
```


**Sources:** communication/mavsdkvehicleserver.cpp49-60

Flight mode changes from the ground station trigger specific autopilot behaviors. The server acts as the coordinator between MAVLink protocol and internal autopilot systems.

**Sources:** communication/mavsdkvehicleserver.cpp80-103

| Component | Setter Method | Signal Connection | Purpose |
|---|---|---|---|
`WaypointFollower` | `setWaypointFollower()` | `startWaypointFollower` → `startFollowingRoute()` | Route following |
`pauseWaypointFollower` → `stop()` | Pause/hold position | ||
`resetWaypointFollower` → `resetState()` | Reset to beginning | ||
`clearRouteOnWaypointFollower` → `clearRoute()` | Clear mission | ||
`FollowPoint` | `setFollowPoint()` | `startFollowPoint` → `startFollowPoint()` | Dynamic target following |
`stopFollowPoint` → `stopFollowPoint()` | Stop following | ||
`MovementController` | `setMovementController()` | (Direct calls) | Manual control actuators |

**Sources:** communication/mavsdkvehicleserver.cpp557-576

The server implements bidirectional mission protocol support, allowing ground stations to upload missions to the vehicle and download the current mission from the vehicle.

**Mission Item to PosPoint Conversion:**

**Sources:** communication/mavsdkvehicleserver.cpp105-121 communication/mavsdkvehicleserver.cpp578-592

The server responds to mission download requests by serializing the current route from the `WaypointFollower`

.

**Message Flow:**

| Step | Message | Handler | Action |
|---|---|---|---|
| 1 | `MISSION_REQUEST_LIST` | `intercept_incoming_messages_async()` | Send `MISSION_COUNT` with route size |
| 2 | `MISSION_REQUEST_INT` or `MISSION_REQUEST` | Message interception | Send `MISSION_ITEM_INT` or `MISSION_ITEM` |
| 3 | `MISSION_ACK` | Message interception | Acknowledge completion |

**Sources:** communication/mavsdkvehicleserver.cpp165-283

When in Manual flight mode, the server processes `MANUAL_CONTROL`

messages and translates them to `MovementController`

commands.

**Normalization:**

**Configuration Parameter:**

`MC_MAX_SPEED_MS`

- Maximum speed for manual control (default: 2.0 m/s)**Sources:** communication/mavsdkvehicleserver.cpp156-163 communication/mavsdkvehicleserver.cpp594-608

The server implements a heartbeat-based safety mechanism that monitors incoming `HEARTBEAT`

messages. If no heartbeat is received within the timeout period, the vehicle stops all motion.

**Timeout Configuration:**

**Recovery:** When heartbeat is restored, the timer resets and normal operation resumes. The vehicle remains stopped until commanded to move again.

**Sources:** communication/mavsdkvehicleserver.cpp138-151 communication/mavsdkvehicleserver.cpp489-507 communication/vehicleserver.h53-58

The server receives RTCM correction data via `GPS_RTCM_DATA`

MAVLink messages and forwards it to the GNSS receiver. Since RTCM packets can exceed MAVLink message size limits, they may be fragmented across multiple messages.

**Fragment Metadata Encoding:**

```
flags byte (8 bits):
- Bit 0: Fragmented flag (1 = fragmented, 0 = complete)
- Bits 1-2: Fragment ID (0-3)
- Bits 3-7: Sequence ID (0-31)
```


**Buffer Management:**

**Sources:** communication/mavsdkvehicleserver.cpp319-350

For vehicles with trailers (truck-trailer combinations), the server creates a separate MAVLink component to represent the trailer state. This enables ground stations to visualize and track both the towing vehicle and the trailer independently.

**Component Creation Conditions:**

**Trailer Component Configuration:**

`ComponentType::Custom`

`VehicleState::getId()`

)`TrailerState::getId()`

**Sources:** communication/mavsdkvehicleserver.cpp476-478 communication/mavsdkvehicleserver.cpp766-828

The trailer component subscribes to the main vehicle's `VehicleState`

updates and publishes its own telemetry:

| Telemetry Item | Source | Published As |
|---|---|---|
| Position | `TrailerState::getPosition()` | `POSITION_TARGET_LOCAL_NED` |
| Velocity | Calculated from trailer kinematics | `VELOCITY_NED` |
| Heading | `TrailerState` yaw angle | `HEADING` |

**Sources:** communication/mavsdkvehicleserver.cpp766-828

The server integrates with `MavlinkParameterServer`

to expose configurable parameters over MAVLink. Parameters can be read and modified by ground stations using the standard MAVLink parameter protocol.

**Registered Parameters:**

| Parameter ID | Type | Getter | Setter | Purpose |
|---|---|---|---|---|
`MC_MAX_SPEED_MS` | Float | `getManualControlMaxSpeed()` | `setManualControlMaxSpeed()` | Maximum manual control speed |
`VEH_WW_OBJ_TYPE` | Int | `getWaywiseObjectType()` | `setWaywiseObjectType()` | Vehicle object type enum |

**Parameter Synchronization:**
When parameters change on the vehicle side, `PARAM_VALUE`

messages are intercepted and the local `ParameterServer`

is updated to maintain consistency.

**Sources:** communication/mavsdkvehicleserver.cpp36-37 communication/mavsdkvehicleserver.cpp441-452 communication/mavsdkvehicleserver.cpp481-487

Beyond standard telemetry, the server publishes custom messages to provide additional autopilot state information to ground stations.

**1. Autopilot Radius ( NAMED_VALUE_FLOAT with name "AR")**

Published at 10 Hz to indicate the current pure pursuit lookahead radius.

**Use Case:** Ground station visualization of the pure pursuit circle.

**Sources:** communication/mavsdkvehicleserver.cpp353-371

**2. Autopilot Target Point ( POSITION_TARGET_LOCAL_NED)**

Published at 10 Hz to indicate the current target/goal point the autopilot is tracking.

**Use Case:** Ground station visualization of the autopilot's current goal point on the route.

**Sources:** communication/mavsdkvehicleserver.cpp374-411

The server processes system-level commands via `COMMAND_LONG`

messages.

**Command: MAV_CMD_DO_SET_MISSION_CURRENT**

`switchAutopilotID(float autopilotID)`

**Command: MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN**

`shutdownOrRebootOnboardComputer(bool isShutdown)`

**Sources:** communication/mavsdkvehicleserver.cpp296-317

The server can forward application logs to ground stations via `STATUSTEXT`

MAVLink messages. This enables remote debugging and monitoring.

Since `STATUSTEXT`

supports only 50 characters per message (minus 8 bytes for MAVLink header overhead = 42 characters effective), long log messages are automatically chunked.

**Chunk Metadata:**

`id`

: Unique message ID (1-65535, wraps around)`chunk_seq`

: Chunk sequence number (0-N)`severity`

: Log severity level (MAV_SEVERITY_*)**Enable/Disable:**

**Sources:** communication/mavsdkvehicleserver.cpp665-743

The server integrates with u-blox GNSS receivers to obtain raw GPS data for telemetry publishing.

**Data Extraction from UBX-NAV-PVT:**

| UBX Field | MAVLink Field | Transformation |
|---|---|---|
`i_tow` | `timestamp_us` | Multiply by 1000 |
`lat` | `latitude_deg` | Direct |
`lon` | `longitude_deg` | Direct |
`height` | `absolute_altitude_m` | Direct |
`p_dop` | `hdop` , `vdop` | Direct (approximation) |
`vel_n/e/d` | `velocity_m_s` | Calculate magnitude |
`head_mot` | `cog_deg` | Direct |
`h_acc` | `horizontal_uncertainty_m` | Direct |
`v_acc` | `vertical_uncertainty_m` | Direct |
`head_veh` | `yaw_deg` | Direct |
`num_sv` | `num_satellites` | Direct |
`fix_type` , `carr_soln` | `fix_type` | Map to enum (NoFix, 2D, 3D, RTK Float, RTK Fixed) |

**Sources:** communication/mavsdkvehicleserver.cpp509-549

The server intercepts outgoing `HEARTBEAT`

messages to customize vehicle type and autopilot identification for proper ground station recognition.

**Customization by Component:**

| Component ID | Type | Autopilot | Mode Flags |
|---|---|---|---|
`MAV_COMP_ID_AUTOPILOT1` | `MAV_TYPE_GROUND_ROVER` | `WAYWISE_MAVLINK_AUTOPILOT_ID` | Safety armed, custom mode enabled |
`MAV_COMP_ID_CAMERA` | `MAV_TYPE_CAMERA` | `MAV_AUTOPILOT_INVALID` | Default |

**Sources:** communication/mavsdkvehicleserver.cpp414-458

| Entity | Type | Purpose |
|---|---|---|
`MavsdkVehicleServer` | Class | Main vehicle-side MAVLink server |
`mavsdk::Mavsdk` | MAVSDK Core | MAVLink system instance |
`mavsdk::TelemetryServer` | Plugin | Publishes position/velocity telemetry |
`mavsdk::ActionServer` | Plugin | Handles flight mode and arming |
`mavsdk::MissionRawServer` | Plugin | Handles mission upload |
`mavsdk::MavlinkPassthrough` | Plugin | Custom message handling |
`MavlinkParameterServer` | Singleton | Parameter protocol implementation |
`mPublishMavlinkTimer` | QTimer | 10 Hz telemetry publishing |
`mHeartbeatTimer` | QTimer | 2-second safety timeout |
`convertMissionItemToPosPoint()` | Method | Converts MAVLink mission items to internal format |
`handleManualControlMessage()` | Method | Processes manual control inputs |
`updateRawGpsAndGpsInfoFromUbx()` | Method | Extracts GPS data from u-blox NAV-PVT |
`heartbeatTimeout()` | Method | Safety stop on connection loss |
`createMavsdkComponentForTrailer()` | Method | Multi-body vehicle support |

**Sources:** communication/mavsdkvehicleserver.h1-73 communication/mavsdkvehicleserver.cpp1-828

Refresh this wiki
