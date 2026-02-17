# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/1-overview

WayWise is an autonomous vehicle control and navigation system implementing MAVLink-based communication for ground vehicles (cars, articulated truck-trailer combinations) and multicopters. The system supports dual deployment: autopilot logic executes either onboard the vehicle via `MavsdkVehicleServer`

communication/mavsdkvehicleserver.h24-71 or remotely via `MavsdkVehicleConnection`

communication/vehicleconnections/mavsdkvehicleconnection.h32-114

**Vehicle Models**:

`CarState`

- Ackermann steering with bicycle kinematic model vehicles/carstate.h20-66`TruckState`

- Articulated vehicles with `mTrailingVehicle`

support vehicles/truckstate.h13-57`TrailerState`

- Passive trailers with angle tracking vehicles/trailerstate.h19-52`CopterState`

- Quadcopters with landed state management vehicles/copterstate.h14-38**Autopilot Implementations**:

`PurepursuitWaypointFollower`

- Path tracking via pure pursuit algorithm with 50ms update rate autopilot/purepursuitwaypointfollower.cpp16-21`FollowPoint`

- Dynamic target following with heartbeat timeout autopilot/followpoint.cpp11-30`MultiWaypointFollower`

- Route switching between multiple `WaypointFollower`

instances autopilot/multiwaypointfollower.h17-63**Sensor Integration**:

`UbloxRover`

- u-blox ZED-F9P/F9R GNSS receivers with RTK corrections sensors/gnss/ubloxrover.h`SDVPVehiclePositionFuser`

- Sensor fusion combining GNSS, IMU, and odometry sensors/positionfusion/sdvpvehiclepositionfuser.h`MavsdkGimbal`

- Camera gimbal control via MAVLink GIMBAL_MANAGER protocol sensors/camera/mavsdkgimbal.h**Communication Layer**:

`MavsdkStation`

- Vehicle discovery via `mMavsdk->subscribe_on_new_system()`

communication/mavsdkstation.cpp`ParameterServer`

with getter/setter callbacks communication/parameterserver.hWayWise enables two deployment configurations determined by where the `PurepursuitWaypointFollower`

instance executes:

**Configuration 1: Onboard Autopilot**

**Configuration 2: Remote Autopilot**

The deployment mode is determined by constructor arguments:

`PurepursuitWaypointFollower(QSharedPointer<MovementController>)`

- Onboard mode autopilot/purepursuitwaypointfollower.cpp16-21`PurepursuitWaypointFollower(QSharedPointer<VehicleConnection>, PosType)`

- Remote mode autopilot/purepursuitwaypointfollower.cpp23-29The `isOnVehicle()`

method determines control output:

`true`

: Calls `mMovementController->setDesiredSteeringCurvature()`

autopilot/purepursuitwaypointfollower.cpp392-396`false`

: Calls `mVehicleConnection->requestVelocityAndYaw()`

autopilot/purepursuitwaypointfollower.cpp399-409Sources: autopilot/purepursuitwaypointfollower.cpp16-29 autopilot/purepursuitwaypointfollower.cpp380-411 communication/mavsdkvehicleserver.cpp15-29 communication/vehicleconnections/mavsdkvehicleconnection.cpp9-36

WayWise uses MAVLink 2.0 protocol via the MAVSDK library for vehicle-ground station communication:

**Ground Station Side: MavsdkStation and MavsdkVehicleConnection**

**Vehicle Side: MavsdkVehicleServer**

Sources: communication/mavsdkstation.cpp communication/vehicleconnections/mavsdkvehicleconnection.cpp9-291 communication/mavsdkvehicleserver.cpp15-479

`VehicleState`

maintains independent position estimates from multiple sensors via the `mPositionBySource`

array:

**Position Type Enumeration** core/pospoint.h:

**Storage and Access**:

**Autopilot Usage**:
`PurepursuitWaypointFollower`

selects position source via `mPosTypeUsed`

member autopilot/purepursuitwaypointfollower.h110:

`PosType::fused`

(sensor fusion output)`setPosTypeUsed(PosType)`

autopilot/purepursuitwaypointfollower.cpp418-421**Position Update Flow**:

Sources: core/pospoint.h vehicles/vehiclestate.h25-148 vehicles/objectstate.cpp55-58 autopilot/purepursuitwaypointfollower.h110

**Pure Pursuit Algorithm Execution** (50ms update cycle):

**State Machine Transitions** autopilot/purepursuitwaypointfollower.h21:

`NONE`

→ `FOLLOW_ROUTE_INIT`

(via `startFollowingRoute()`

)`FOLLOW_ROUTE_INIT`

→ `FOLLOW_ROUTE_GOTO_BEGIN`

`FOLLOW_ROUTE_GOTO_BEGIN`

→ `FOLLOW_ROUTE_FOLLOWING`

(first waypoint within `purePursuitRadius()`

)`FOLLOW_ROUTE_FOLLOWING`

→ `FOLLOW_ROUTE_APPROACHING_END_GOAL`

(last waypoint)`FOLLOW_ROUTE_APPROACHING_END_GOAL`

→ `FOLLOW_ROUTE_FINISHED`

(distance < `mEndGoalAlignmentThreshold`

)**Key Parameters**:

`mUpdateStatePeriod_ms = 50`

- Control loop frequency autopilot/purepursuitwaypointfollower.h115`mCurrentState.numWaypointsLookahead = 8`

- Lookahead window size autopilot/purepursuitwaypointfollower.h31`mEndGoalAlignmentThreshold = 0.1`

- Goal reached tolerance in meters autopilot/purepursuitwaypointfollower.h123Sources: autopilot/purepursuitwaypointfollower.cpp183-411 autopilot/purepursuitwaypointfollower.h21-35 vehicles/vehiclestate.cpp93-107

WayWise uses three coordinate frames with explicit transformations:

**ENU (East-North-Up)** - Primary planning frame:

`llh_t mEnuReference`

in `VehicleState`

vehicles/objectstate.h87`setEnuRef(llh_t)`

vehicles/objectstate.cpp60-65**LLH (Latitude-Longitude-Height)** - Global WGS-84:

`coordinateTransforms::llhToEnu()`

, `coordinateTransforms::enuToLlh()`

core/coordinatetransforms.h**NED (North-East-Down)** - MAVLink standard:

`MavsdkVehicleServer::mPublishMavlinkTimer`

communication/mavsdkvehicleserver.cpp49-78:
**Vehicle Frame** - Body-fixed coordinate system:

`coordinateTransforms::ENUToVehicleFrame(point, position, yaw)`

vehicles/vehiclestate.cpp102-107`curvature = -2*y/(x²+y²)`

vehicles/vehiclestate.cpp93-100Sources: core/coordinatetransforms.h vehicles/objectstate.h87 vehicles/objectstate.cpp60-65 communication/mavsdkvehicleserver.cpp49-78 vehicles/vehiclestate.cpp93-107

WayWise organizes functionality into subsystem directories:

| Subsystem | Key Components | Description |
|---|---|---|
Communication | `MavsdkStation` , `MavsdkVehicleConnection` , `MavsdkVehicleServer` , `ParameterServer` | MAVLink protocol handling, vehicle discovery, parameter management |
Autopilot | `PurepursuitWaypointFollower` , `FollowPoint` , `MultiWaypointFollower` , `EmergencyBrake` | Path tracking algorithms, safety systems |
Vehicle State | `VehicleState` , `CarState` , `TruckState` , `TrailerState` , `CopterState` | Kinematics, multi-source positioning, vehicle hierarchy |
Sensors | `UbloxRover` , `UbloxBasestation` , `SDVPVehiclePositionFuser` , `MavsdkGimbal` | GNSS/RTK, sensor fusion, camera control |
User Interface | `MapWidget` , `DriveUI` , `FlyUI` , `PlanUI` , `CameraGimbalUI` | Qt-based visualization and control |
Core Utilities | `PosPoint` , `coordinateTransforms` , `geometry` | Data structures, coordinate systems, geometric calculations |

**Class Inheritance Hierarchies**:

Sources: vehicles/objectstate.h31-100 vehicles/vehiclestate.h25-133 vehicles/carstate.h20-66 vehicles/truckstate.h13-57 communication/vehicleconnections/vehicleconnection.h22-115 communication/vehicleserver.h19-63 autopilot/purepursuitwaypointfollower.h42-127 autopilot/multiwaypointfollower.h17-65

**Heartbeat Monitoring** communication/mavsdkvehicleserver.cpp139-155:

`mHeartbeatTimer`

configured as single-shot timer with 2000ms timeout communication/mavsdkvehicleserver.h61`MAVLINK_MSG_ID_HEARTBEAT`

message receipt`heartbeatTimeout()`

communication/mavsdkvehicleserver.cpp489-501:
**Emergency Brake System** autopilot/emergencybrake.h:

`EmergencyBrake`

class processes sensor inputs (camera, lidar, radar)`WaypointFollower`

via signals:
`activateEmergencyBrake()`

signal autopilot/waypointfollower.h`deactivateEmergencyBrake()`

signal`startFollowingRoute()`

called autopilot/purepursuitwaypointfollower.cpp126**Speed Limit Regions** autopilot/purepursuitwaypointfollower.cpp386-390:

`loadSpeedLimitRegionsFile()`

autopilot/purepursuitwaypointfollower.cpp570-644`isPointWithin()`

from `routeutils`

routeplanning/routeutils.h**FollowPoint Timeout** autopilot/followpoint.cpp44-58:

`mFollowPointHeartbeatTimer`

requires continuous point updates`stopFollowPoint()`

with position holdSources: communication/mavsdkvehicleserver.cpp139-501 autopilot/emergencybrake.h autopilot/purepursuitwaypointfollower.cpp126-644 autopilot/followpoint.cpp44-58

**ControlTower Application** - Desktop ground control station:

`MavsdkStation`

for vehicle discovery`PurepursuitWaypointFollower`

instances`MapWidget`

, `DriveUI`

, `FlyUI`

, `PlanUI`

**RCCar Application** - Onboard vehicle implementation:

`MavsdkVehicleServer`

as MAVLink autopilot`UbloxRover`

(ZED-F9R) with `SDVPVehiclePositionFuser`

`MovementController`

for VESC motor control`TruckState`

with optional `TrailerState`

**Example Applications** examples:

`RCCar_MAVLINK_autopilot`

- Simulated vehicle with `MavsdkVehicleServer`

`RCCar_ISO22133_autopilot`

- ISO/TS 22133:2023 protocol implementation`map_local_twocars`

- Multi-vehicle visualization example**Build Dependencies**:

WayWise is designed as a git submodule for integration into larger projects. The API evolves continuously and does not provide versioned releases.

**ControlTower** - Desktop ground control station:

`MavsdkStation`

to discover vehicles`MapWidget`

visualization with multiple vehicles`DriveUI`

, `FlyUI`

, `PlanUI`

, `CameraGimbalUI`

interfaces`PurepursuitWaypointFollower`

instances**RCCar** - RC car with GNSS/IMU:

`MavsdkVehicleServer`

as onboard autopilot`UbloxRover`

(ZED-F9R) with ESF sensor fusion`MovementController`

with VESC motor controller`TruckState`

with optional `TrailerState`

**WayWiseR** - ROS2 integration:

The `/examples`

directory contains minimal implementations:

**RCCar with MAVLink Autopilot**:

`CarState`

vehicle`MavsdkVehicleServer`

listening on UDP port 14540`PurepursuitWaypointFollower`

with `MovementController`

**RCCar with ISO22133 Autopilot**:

For detailed documentation on subsystems:

Sources: communication/mavsdkvehicleserver.cpp15-29 autopilot/purepursuitwaypointfollower.cpp17-31 vehicles/truckstate.h13-17

WayWise has its roots in the RISE Self-Driving Vehicle Platform (SDVP), but was redesigned and rewritten based on C++ and Qt targeting commercial off-the-shelf hardware. It is actively maintained by the RISE Dependable Transport Systems group and continuously evolves to support new research use cases.

Sources: README.md8-9 README.md19-27

Refresh this wiki
