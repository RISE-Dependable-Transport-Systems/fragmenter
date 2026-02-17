# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/2-communication-layer

The Communication Layer implements the MAVLink-based communication architecture that enables WayWise to operate in three deployment modes: vehicle-side autopilot, ground station control, and hybrid configurations. This page documents the three core components (`MavsdkStation`

, `MavsdkVehicleConnection`

, `MavsdkVehicleServer`

), their interactions, and the MAVLink protocol handling.

For specific details about:

The Communication Layer provides a bidirectional MAVLink communication bridge between ground control stations and autonomous vehicles. It uses the MAVSDK library for protocol handling and supports both UDP and serial connections.

**Diagram: Communication Layer Three-Component Architecture**

Sources: communication/vehicleconnections/mavsdkstation.h1-56 communication/mavsdkvehicleserver.h1-73 communication/vehicleconnections/mavsdkvehicleconnection.h1-116

The three components are:

| Component | Location | Primary Role | Key Classes |
|---|---|---|---|
MavsdkStation | Ground Station | Vehicle discovery, connection lifecycle management, RTCM broadcasting | `MavsdkStation` |
MavsdkVehicleConnection | Ground Station | Per-vehicle interface, telemetry subscription, command sending | `MavsdkVehicleConnection` , `VehicleConnection` |
MavsdkVehicleServer | Vehicle Onboard | MAVLink server, telemetry publishing, command handling | `MavsdkVehicleServer` , `VehicleServer` |

Sources: communication/vehicleconnections/mavsdkstation.cpp1-132 communication/vehicleconnections/mavsdkvehicleconnection.cpp1-1283 communication/mavsdkvehicleserver.cpp1-1040

WayWise supports three deployment configurations:

**Vehicle-Side Autopilot**: `MavsdkVehicleServer`

runs on vehicle with local `WaypointFollower`

and `MovementController`

. Ground station provides monitoring and route upload only.

**Ground Station Autopilot**: `MavsdkVehicleConnection`

runs connection-local `WaypointFollower`

that sends velocity commands via MAVLink offboard mode.

**Hybrid**: Both vehicle and ground station have autopilots, switchable via `MAV_CMD_DO_SET_MISSION_CURRENT`

command.

Sources: communication/vehicleconnections/vehicleconnection.cpp1-130 communication/mavsdkvehicleserver.cpp15-30 communication/vehicleconnections/mavsdkvehicleconnection.cpp9-37

**Diagram: Communication Layer Class Hierarchy**

Sources: communication/vehicleserver.h1-63 communication/mavsdkvehicleserver.h1-73 communication/vehicleconnections/vehicleconnection.h1-115 communication/vehicleconnections/mavsdkvehicleconnection.h1-116 communication/vehicleconnections/mavsdkstation.h1-56

`MavsdkStation`

acts as the central hub on the ground station computer. It listens for incoming MAVLink connections and manages the lifecycle of multiple vehicle connections.

**Diagram: MavsdkStation Vehicle Discovery Sequence**

Sources: communication/vehicleconnections/mavsdkstation.cpp9-131

Key implementation details:

**UDP Connection** - communication/vehicleconnections/mavsdkstation.cpp23-34:

**Serial Connection** - communication/vehicleconnections/mavsdkstation.cpp36-46:

Sources: communication/vehicleconnections/mavsdkstation.cpp23-46

`MavsdkStation`

monitors heartbeats from all connected vehicles with a 5-second timeout threshold:

| Timer Interval | Timeout Threshold | Action on Timeout |
|---|---|---|
| 1 second | 5 seconds | Remove from `mVehicleConnectionMap` , emit `disconnectOfVehicleConnection` |

**Heartbeat Logic** - communication/vehicleconnections/mavsdkstation.cpp70-91:

Sources: communication/vehicleconnections/mavsdkstation.cpp70-91 communication/vehicleconnections/mavsdkstation.h50-52

The station broadcasts RTCM correction data to all connected vehicles:

**Broadcast Implementation** - communication/vehicleconnections/mavsdkstation.cpp48-53:

This enables RTK positioning by distributing corrections from a base station to all rovers. See GNSS & RTK Positioning for details on RTCM handling.

Sources: communication/vehicleconnections/mavsdkstation.cpp48-53

`MavsdkVehicleConnection`

provides the ground station's interface to a single vehicle. It subscribes to telemetry, sends commands, and manages coordinate transformations.

**Diagram: MavsdkVehicleConnection Initialization Flow**

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp9-291

**Car State Setup** - communication/vehicleconnections/mavsdkvehicleconnection.cpp293-317:
Retrieves parameters: `VEH_LENGTH`

, `VEH_WIDTH`

, `VEH_WHLBASE`

, `VEH_RA2CO_X`

, `VEH_RA2REO_X`


**Truck State Setup** - communication/vehicleconnections/mavsdkvehicleconnection.cpp319-382:
Extends car setup with: `VEH_RA2HO_X`

(hitch offset), `TRLR_COMP_ID`

(trailer component)

If trailer detected, subscribes to `MAVLINK_MSG_ID_NAMED_VALUE_FLOAT`

with name `"TRLR_YAW"`

to track trailer angle.

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp293-382

| Telemetry Type | MAVSDK Plugin Method | Purpose | Update Handler |
|---|---|---|---|
| Position | `subscribe_position()` or `subscribe_position_velocity_ned()` | Vehicle location | Convert to ENU, update `VehicleState` |
| Heading | `subscribe_heading()` | Yaw angle | Convert NED→ENU, update position yaw |
| Velocity | `subscribe_velocity_ned()` | Speed vector | Convert NED→ENU, update velocity |
| Battery | `subscribe_battery()` | Power status | Emit `updatedBatteryState` signal |
| Armed | `subscribe_armed()` | Safety state | Update `VehicleState::setIsArmed()` |
| Home Position | `subscribe_home()` | Reference point | Convert to ENU, update home position |
| Flight Mode | `subscribe_flight_mode()` | Control mode | Update state, stop autopilot if needed |
| Landed State | `subscribe_landed_state()` | Copter only | Update `CopterState::setLandedState()` |

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp84-160

`MavsdkVehicleConnection`

manages two key coordinate systems:

**ENU Reference ( mEnuReference)** - communication/vehicleconnections/mavsdkvehicleconnection.cpp384-387:

`setEnuReference()`

**GPS Global Origin ( mGpsGlobalOrigin)** - communication/vehicleconnections/mavsdkvehicleconnection.cpp664-673:

For coordinate transformation details, see Coordinate Systems & Transformations.

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp384-387 communication/vehicleconnections/mavsdkvehicleconnection.cpp664-673

**Flight Commands** - communication/vehicleconnections/mavsdkvehicleconnection.cpp415-478:

`requestArm()`

, `requestDisarm()`

- Use `Action`

plugin`requestTakeoff()`

, `requestLanding()`

, `requestReturnToHome()`

- Use `Action`

plugin`requestPrecisionLanding()`

- Uses `MavlinkPassthrough`

to set PX4 mode`requestManualControl()`

- Changes flight mode via `MAV_CMD_DO_SET_MODE`

**Position Commands**:

`requestGotoLlh()`

- communication/vehicleconnections/mavsdkvehicleconnection.cpp514-536 - Uses `Action::goto_location_async()`

or `MAV_CMD_DO_REPOSITION`

`requestGotoENU()`

- communication/vehicleconnections/mavsdkvehicleconnection.cpp538-546 - Converts ENU→LLH then calls `requestGotoLlh()`

`requestVelocityAndYaw()`

- communication/vehicleconnections/mavsdkvehicleconnection.cpp548-564 - Uses `Offboard`

plugin for velocity controlSources: communication/vehicleconnections/mavsdkvehicleconnection.cpp415-564

RTCM correction data is forwarded to vehicles via `GPS_RTCM_DATA`

MAVLink messages - communication/vehicleconnections/mavsdkvehicleconnection.cpp566-615:

**Fragmentation Logic**:

`GPS_RTCM_DATA`

message**Fragment Structure**:

```
flags = 1 | (fragmentId << 1) | (sequenceId << 3)
```


Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp566-615

`MavsdkVehicleServer`

runs on the vehicle's onboard computer and acts as a MAVLink autopilot, publishing telemetry and handling commands.

**Server Setup** - communication/mavsdkvehicleserver.cpp15-45:

Sources: communication/mavsdkvehicleserver.cpp15-45

The server publishes telemetry at 10 Hz (100ms timer) - communication/mavsdkvehicleserver.cpp48-78:

**Published Messages**:

`POSITION_VELOCITY_NED`

- Position and velocity in NED frame (converted from ENU)`POSITION`

(LLH) - Global position`HOME`

- Home position`RAW_GPS`

- Raw GNSS data (if UbloxRover connected)`GPS_GLOBAL_ORIGIN`

- ENU reference point**Coordinate Conversion** - communication/mavsdkvehicleserver.cpp49-54:

Sources: communication/mavsdkvehicleserver.cpp48-78

**Diagram: MavsdkVehicleServer Command Handling Flow**

Sources: communication/mavsdkvehicleserver.cpp80-608

**Flight Mode Subscription** - communication/mavsdkvehicleserver.cpp80-103:

`WaypointFollower`

`FollowPoint`

**Mission Upload** - communication/mavsdkvehicleserver.cpp105-129:

`MissionPlan`

from `MissionRawServer`

`MissionItem`

to `PosPoint`

`WaypointFollower`

**Manual Control** - communication/mavsdkvehicleserver.cpp594-608:

`MANUAL_CONTROL`

message`x`

) by `mManualControlMaxSpeed`

`r`

) directly`WaypointFollower`

Sources: communication/mavsdkvehicleserver.cpp80-608

The server receives and reassembles RTCM data from `GPS_RTCM_DATA`

messages - communication/mavsdkvehicleserver.cpp319-350:

**Defragmentation Logic**:

The reconstructed RTCM data is forwarded to `UbloxRover`

for RTK corrections.

Sources: communication/mavsdkvehicleserver.cpp319-350

The server implements a heartbeat timeout safety mechanism - communication/mavsdkvehicleserver.cpp139-507:

| Component | Timeout | Action on Timeout |
|---|---|---|
| Heartbeat Monitor | 2 seconds | Stop `WaypointFollower` , set speed/steering to 0 |
| Heartbeat Filter | Active until first heartbeat | Drop all incoming messages except `HEARTBEAT` |

**Implementation** - communication/mavsdkvehicleserver.cpp144-151:

Sources: communication/mavsdkvehicleserver.cpp139-507

For truck-trailer combinations, the server creates a separate MAVLink component - communication/mavsdkvehicleserver.cpp766-823:

**Trailer Component Creation**:

`TrailerState::getId()`

)`NAMED_VALUE_FLOAT`

with name `"TRLR_YAW"`

containing trailer yaw angle`MAV_TYPE_UNKNOWN`

This enables ground stations to track and visualize trailer state independently.

Sources: communication/mavsdkvehicleserver.cpp766-823

| Message | Direction | Frequency | Purpose | Handler |
|---|---|---|---|---|
`HEARTBEAT` | Bidirectional | 1 Hz | Connection monitoring, vehicle discovery | `MavsdkStation::handleNewMavsdkSystem()` |
`POSITION_VELOCITY_NED` | Vehicle→GCS | 10 Hz | Position and velocity telemetry | `Telemetry::subscribe_position_velocity_ned()` |
`GPS_RAW_INT` | Vehicle→GCS | 10 Hz | Raw GNSS data | Published via `TelemetryServer::publish_raw_gps()` |
`GPS_RTCM_DATA` | GCS→Vehicle | Variable | RTK correction data | `MavsdkVehicleServer` intercept, emit `rxRtcmData` |
`MANUAL_CONTROL` | GCS→Vehicle | Variable | Joystick/keyboard input | `MavsdkVehicleServer::handleManualControlMessage()` |
`COMMAND_LONG` | GCS→Vehicle | On-demand | Flight commands, mode changes | `ActionServer` or `MavlinkPassthrough` |
`MISSION_ITEM_INT` | Bidirectional | On-demand | Waypoint upload/download | `MissionRawServer` and custom handlers |
`NAMED_VALUE_FLOAT` | Vehicle→GCS | 10 Hz | Custom values (autopilot radius, trailer yaw) | `MavlinkPassthrough::subscribe_message()` |
`POSITION_TARGET_LOCAL_NED` | Vehicle→GCS | 10 Hz | Autopilot target/reference points | `MavlinkPassthrough::subscribe_message()` |
`GPS_GLOBAL_ORIGIN` | Vehicle→GCS | 10 Hz | ENU reference point | Published via `MavsdkVehicleServer::sendGpsOriginLlh()` |

Sources: communication/mavsdkvehicleserver.cpp48-411 communication/vehicleconnections/mavsdkvehicleconnection.cpp166-279

**Diagram: Route Upload Message Sequence**

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp859-916 communication/mavsdkvehicleserver.cpp105-136

For downloading the current route from vehicle to ground station - communication/mavsdkvehicleserver.cpp165-282:

`MISSION_REQUEST_LIST`

`mWaypointFollower->getCurrentRoute()`

`MISSION_COUNT`

`MISSION_REQUEST_INT`

or `MISSION_REQUEST`

`PosPoint`

to `MISSION_ITEM_INT`

/`MISSION_ITEM`

and sends`MISSION_ACK`

Sources: communication/mavsdkvehicleserver.cpp165-282

WayWise supports two autopilot locations, selectable at runtime:

**Diagram: Dual-Path Autopilot Decision Flow**

Sources: communication/vehicleconnections/vehicleconnection.cpp25-64

**API** - communication/vehicleconnections/vehicleconnection.cpp7-14:

Once set, all autopilot operations (start, stop, pause, etc.) operate on the local instance.

**Implementation** - communication/vehicleconnections/vehicleconnection.cpp25-64:

| Operation | Local Path | Vehicle Path |
|---|---|---|
`isAutopilotActive()` | `mWaypointFollower->isActive()` | `isAutopilotActiveOnVehicle()` via MAVLink |
`startAutopilot()` | `mWaypointFollower->startFollowingRoute(false)` | `startAutopilotOnVehicle()` via mode change |
`stopAutopilot()` | `mWaypointFollower->stop()` + `resetState()` | `stopAutopilotOnVehicle()` via mode change |
`clearRoute()` | `mWaypointFollower->clearRoute()` | `clearRouteOnVehicle()` via `MISSION_CLEAR_ALL` |
`appendToRoute()` | `mWaypointFollower->addRoute()` | `appendToRouteOnVehicle()` via mission protocol |

Sources: communication/vehicleconnections/vehicleconnection.cpp25-87

Multiple autopilots on the vehicle can be switched using `MAV_CMD_DO_SET_MISSION_CURRENT`

with `param3`

as autopilot ID - communication/mavsdkvehicleserver.cpp298-304:

The application connects this signal to switch between different `WaypointFollower`

instances.

Sources: communication/mavsdkvehicleserver.cpp296-316

The Communication Layer integrates with `ParameterServer`

for configuration synchronization. Parameters can be:

`MavsdkVehicleServer::provideParametersToParameterServer()`

`MavsdkVehicleConnection::getIntParameterFromVehicle()`

, etc.`MavsdkVehicleConnection::setFloatParameterOnVehicle()`

, etc.Parameter synchronization uses MAVLink's `PARAM_VALUE`

, `PARAM_SET`

, `PARAM_REQUEST_READ`

messages. See Parameter Server for details.

Sources: communication/mavsdkvehicleserver.cpp481-487 communication/vehicleconnections/mavsdkvehicleconnection.cpp1147-1248

The `SerialPortDialog`

provides a UI for selecting serial connections - userinterface/serialportdialog.cpp1-59:

**Features**:

`selectedSerialPort(QSerialPortInfo, baudrate)`

signal**Usage**:

Sources: userinterface/serialportdialog.cpp1-59 userinterface/serialportdialog.h1-40

Refresh this wiki
