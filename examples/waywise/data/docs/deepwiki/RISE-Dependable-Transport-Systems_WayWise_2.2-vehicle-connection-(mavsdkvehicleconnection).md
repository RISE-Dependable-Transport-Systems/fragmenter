# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/2.2-vehicle-connection-(mavsdkvehicleconnection)

`MavsdkVehicleConnection`

is the ground station's interface for communicating with remote vehicles over MAVLink protocol using the MAVSDK library. This class provides the primary abstraction layer between the WayWise ground control station and MAVLink-based vehicles, handling vehicle discovery, state management, command execution, and telemetry reception.

This page covers the ground station side of the communication system. For vehicle-side MAVLink handling, see Vehicle Server (MavsdkVehicleServer). For the discovery and connection management layer, see Ground Station (MavsdkStation).

Sources: communication/vehicleconnections/mavsdkvehicleconnection.h1-116 communication/vehicleconnections/mavsdkvehicleconnection.cpp1-291

Sources: communication/vehicleconnections/vehicleconnection.h22-114 communication/vehicleconnections/mavsdkvehicleconnection.h32-114

`MavsdkVehicleConnection`

supports two distinct autopilot execution models, allowing flexibility in system deployment:

**Connection-Local Path**: Autopilot logic executes on the ground station. The `WaypointFollower`

or `FollowPoint`

instance sends position/velocity commands to the vehicle via `MavsdkVehicleConnection`

. This mode is set by calling `setWaypointFollowerConnectionLocal()`

or `setFollowPointConnectionLocal()`

.

**On-Vehicle Path**: Autopilot logic executes on the vehicle. Routes are uploaded as MAVLink missions, and the vehicle's `MavsdkVehicleServer`

manages a `PurepursuitWaypointFollower`

instance that runs locally on the vehicle.

The `VehicleConnection`

base class provides unified methods (`startAutopilot()`

, `pauseAutopilot()`

, etc.) that automatically route to the appropriate implementation based on whether a local autopilot is configured.

Sources: communication/vehicleconnections/vehicleconnection.cpp7-129 communication/vehicleconnections/vehicleconnection.h70-107

Upon construction, `MavsdkVehicleConnection`

receives a `MAV_TYPE`

enum from the discovery process and creates the appropriate `VehicleState`

subclass:

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp9-291

The initialization process queries vehicle-specific parameters to configure the state object:

| Parameter Name | Type | Used For | Vehicle Type |
|---|---|---|---|
`VEH_WW_OBJ_TYPE` | int | Distinguish car vs. truck | Ground Rover |
`VEH_LENGTH` | float | Vehicle length | Car/Truck |
`VEH_WIDTH` | float | Vehicle width | Car/Truck |
`VEH_WHLBASE` | float | Wheelbase (axis distance) | Car/Truck |
`VEH_RA2CO_X` | float | Rear axle to center offset | Car/Truck |
`VEH_RA2REO_X` | float | Rear axle to rear end offset | Car/Truck |
`VEH_RA2HO_X` | float | Rear axle to hitch offset | Truck |
`TRLR_COMP_ID` | int | Trailer component ID | Truck |
`TRLR_LENGTH` | float | Trailer length | Trailer |
`TRLR_WIDTH` | float | Trailer width | Trailer |
`TRLR_WHLBASE` | float | Trailer wheelbase | Trailer |
`TRLR_RA2CO_X` | float | Trailer rear axle to center offset | Trailer |
`TRLR_RA2REO_X` | float | Trailer rear axle to rear end offset | Trailer |
`TRLR_RA2HO_X` | float | Trailer rear axle to hitch offset | Trailer |
`PP_EGA_TYPE` | int | End goal alignment type | Ground Rover with autopilot |

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp293-382

For trucks configured with trailers, the system monitors for trailer component announcements:

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp319-382

`MavsdkVehicleConnection`

handles transformations between three coordinate reference frames:

**ENU Reference** (`mEnuReference`

): The ground station's local coordinate system origin, configured by the operator. All internal ground station operations (map display, route planning, autopilot commands) use ENU coordinates relative to this reference.

**GPS Global Origin** (`mGpsGlobalOrigin`

): The vehicle's internal EKF origin in NED frame. This is queried once at startup via `pollCurrentENUreference()`

and is used for landing target calculations and understanding the vehicle's internal reference.

Sources: communication/vehicleconnections/mavsdkvehicleconnection.h80-83 communication/vehicleconnections/mavsdkvehicleconnection.cpp384-952

The class handles incoming position telemetry differently based on vehicle type:

**Ground Rovers** (assumption: WayWise on vehicle side, shared ENU reference):

`position_velocity_ned`

telemetry**Multicopters** (assumption: PX4 on vehicle side, independent reference):

`position`

telemetry (global LLH)`mEnuReference`

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp107-127

`MavsdkVehicleConnection`

utilizes multiple MAVSDK plugins for structured MAVLink communication:

| Plugin | Purpose | Key Methods | Initialized When |
|---|---|---|---|
`mTelemetry` | Receive vehicle state updates | `subscribe_battery()` , `subscribe_position()` , `subscribe_velocity_ned()` , `subscribe_heading()` , `subscribe_flight_mode()` , `subscribe_armed()` , `subscribe_home()` | Constructor |
`mAction` | Execute basic vehicle commands | `arm_async()` , `disarm_async()` , `takeoff_async()` , `land_async()` , `return_to_launch_async()` , `goto_location_async()` , `set_actuator_async()` | Constructor |
`mParam` | Access vehicle parameters | `get_param_int()` , `set_param_int()` , `get_param_float()` , `set_param_float()` , `get_all_params()` | Constructor |
`mMavlinkPassthrough` | Send/receive custom messages | `subscribe_message()` , `queue_message()` , `send_command_long()` , `send_command_int()` | Constructor |
`mOffboard` | Control via velocity setpoints | `set_velocity_ned()` , `start()` , `is_active()` | First call to `requestVelocityAndYaw()` |
`mMissionRaw` | Manage mission waypoints | `upload_mission_async()` , `start_mission_async()` , `pause_mission()` , `clear_mission()` | First autopilot command |

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp13-290 communication/vehicleconnections/mavsdkvehicleconnection.h85-93

The constructor establishes numerous telemetry subscriptions that continuously update the vehicle state:

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp84-160

Beyond standard telemetry, the class subscribes to specific MAVLink messages via `MavlinkPassthrough`

:

**HEARTBEAT** (`MAVLINK_MSG_ID_HEARTBEAT`

): Emits `gotHeartbeat(system_id)`

signal for connection monitoring.

**STATUSTEXT** (`MAVLINK_MSG_ID_STATUSTEXT`

): Receives text messages from vehicle, assembles multi-chunk messages, and logs them with appropriate severity levels (DEBUG, INFO, WARNING, CRITICAL, EMERGENCY).

**NAMED_VALUE_FLOAT** (`MAVLINK_MSG_ID_NAMED_VALUE_FLOAT`

):

`setAutopilotRadius()`

**POSITION_TARGET_LOCAL_NED** (`MAVLINK_MSG_ID_POSITION_TARGET_LOCAL_NED`

): Receives autopilot target point for visualization, converts from NED to ENU, and updates `setAutopilotTargetPoint()`

.

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp166-279

The class provides methods for fundamental vehicle operations:

**Type-Specific Operations**: `requestTakeoff()`

, `requestLanding()`

, and `requestReturnToHome()`

verify vehicle type is `MAV_TYPE_QUADROTOR`

before execution, logging warnings for incompatible types.

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp415-478

**Follow Point Mode**: Before switching to offboard follow-point mode, the system automatically pauses any active on-vehicle autopilot to prevent conflicts.

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp480-512

The class provides multiple position command interfaces:

**Goto Commands**: Direct the vehicle to a specific position

`requestGotoLlh(llh, changeFlightmodeToHold)`

: Global coordinates`requestGotoENU(xyz, changeFlightmodeToHold)`

: Local coordinates (converted to LLH if `mConvertLocalPositionsToGlobalBeforeSending`

is true)When `changeFlightmodeToHold`

is false, uses `MAV_CMD_DO_REPOSITION`

to avoid flight mode change. Otherwise uses `Action::goto_location_async()`

.

**Velocity Commands**: Direct velocity control in offboard mode

`requestVelocityAndYaw(velocityENU, yawDeg)`

: Sets velocity setpointSources: communication/vehicleconnections/mavsdkvehicleconnection.cpp514-564

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp748-828

The `convertPosPointToMissionItem()`

method transforms WayWise `PosPoint`

objects into MAVLink mission items:

| PosPoint Field | MissionItem Field | Notes |
|---|---|---|
`getX()` | `x` | Multiplied by 10e4 for encoding |
`getY()` | `y` | Multiplied by 10e4 for encoding |
`getHeight()` | `z` | Direct mapping |
`getSpeed()` | `param1` | Non-standard usage |
`getAttributes()` | `param2` | Non-standard usage |
| Sequence index | `seq` | Incremental from 0 |
| First waypoint | `current` | Set to true for first item |

**Frame Selection**: Ground rovers use `MAV_FRAME_LOCAL_ENU`

(assumes shared ENU reference). Other vehicle types currently throw an exception as global frame conversion is not implemented.

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp725-746

`MavsdkVehicleConnection`

provides type-safe parameter access through the `mParam`

plugin:

**Return Values**: All get operations return a `std::pair<VehicleConnection::Result, value>`

where `Result`

indicates success/failure and value contains the parameter data.

**Result Conversion**: The `convertParamResult()`

method maps MAVSDK `Param::Result`

enum values to `VehicleConnection::Result`

enum values.

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp878-976

`getAllParametersFromVehicle()`

retrieves all vehicle parameters and transforms them into the `ParameterServer::AllParameters`

structure:

**Known Issue**: Lines 925, 931, and 937 contain a workaround for issue #72, where the bulk retrieval values are incorrect. The code re-queries each parameter individually using `get_param_int()`

, `get_param_float()`

, or `get_param_custom()`

to obtain the correct value.

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp914-942

The `inputRtcmData()`

method forwards RTCM correction data from a base station to the vehicle for RTK GNSS positioning:

**Message Structure**:

**Fragmentation**: If RTCM data exceeds `MAVLINK_MSG_GPS_RTCM_DATA_FIELD_DATA_LEN`

(180 bytes), it is split into multiple fragments with incrementing fragment IDs and a common sequence ID.

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp566-615

For precision landing operations, the class can send landing target positions to PX4 autopilots:

**sendLandingTargetLlh(llh)**: Sends target in global coordinates
**sendLandingTargetENU(xyz)**: Sends target in local coordinates (converts to LLH first)

**Implementation Details**:

`mGpsGlobalOrigin`

)`LANDING_TARGET`

message with `MAV_FRAME_LOCAL_NED`

`position_valid = 1`

to indicate position is available**Note**: PX4 requires landing target in NED frame relative to GPS origin, not home position. The `mGpsGlobalOrigin`

polled at startup is used for this conversion.

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp617-662

Direct actuator control is available via `setActuatorOutput(index, value)`

:

This method is typically used for camera-specific controls (zoom, focus, video mode switching) that are mapped to specific actuator channels.

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp688-694

The `setManualControl(x, y, z, r, buttonStateMask)`

method sends manual control inputs (typically from a gamepad or joystick):

**Parameters**:

`x`

, `y`

, `z`

, `r`

: Control axes in range [-1, 1], scaled to [-1000, 1000] for MAVLink`buttonStateMask`

: Bitmask of button states (16 bits)**Message**: Sends `MANUAL_CONTROL`

MAVLink message with target system ID

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp696-713

The `requestRebootOrShutdownOfSystemComponents()`

method sends reboot or shutdown commands to vehicle components:

**SystemComponent Options**:

`Autopilot`

: Targets the flight controller`OnboardComputer`

: Targets the companion computer**ComponentAction Options**:

`DoNothing`

: No action (value 0)`Reboot`

: Restart the component (value 1)`Shutdown`

: Power off the component (value 2)`RebootComponentAndKeepItInTheBootloaderUntilUpgraded`

: Hold in bootloader (value 3)Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp846-876

Two methods manage GPS origin/reference points:

**pollCurrentENUreference()**: Queries the vehicle's GPS global origin (used for internal EKF) via `get_gps_global_origin_async()`

. The result is stored in `mGpsGlobalOrigin`

and emitted as `gotVehicleENUreferenceLlh`

signal.

**sendSetGpsOriginLlh(llh)**: Attempts to set the vehicle's GPS global origin by sending `SET_GPS_GLOBAL_ORIGIN`

message. Note: PX4 1.12 does not update this while flying.

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp664-952

Refresh this wiki
