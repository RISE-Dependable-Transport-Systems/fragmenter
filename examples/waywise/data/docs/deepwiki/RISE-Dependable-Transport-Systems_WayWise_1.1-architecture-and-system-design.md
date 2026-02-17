# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/1.1-architecture-and-system-design

This document describes the high-level architecture of WayWise, focusing on the structural organization of major subsystems and their relationships. It explains the dual deployment model (on-vehicle + desktop control), communication protocols, and core architectural patterns that enable rapid prototyping of connected autonomous vehicles.

For detailed information about specific subsystems:

**Sources:** README.md1-53 communication/mavsdkvehicleserver.h1-72 communication/vehicleconnections/vehicleconnection.h1-116

WayWise is designed around a **dual deployment model** where the same codebase builds both:

The two sides communicate via **MAVLink protocol** (implemented through MAVSDK) or **ISO/TS 22133**, enabling a clean separation between vehicle autonomy and remote operation.

WayWise follows a layered architecture with clear separation of concerns:

**Layer 1 - User Interface:** Specialized UIs for different vehicle types and operations (ground vehicle control via `DriveUI`

, aerial vehicle control via `FlyUI`

, route planning via `PlanUI`

). All interact through the abstract `VehicleConnection`

interface.

**Layer 2 - Communication:** Implements MAVLink-based communication in three modes via `MavsdkStation`

(ground control station), `MavsdkVehicleConnection`

(remote vehicle client), and `MavsdkVehicleServer`

(onboard MAVLink server).

**Layer 3 - Autopilot:** Multiple autopilot strategies implementing the `WaypointFollower`

interface. `PurepursuitWaypointFollower`

provides the main route-following logic, `GotoWaypointFollower`

handles simple navigation, and `FollowPoint`

enables dynamic target tracking. `EmergencyBrake`

provides safety overlay.

**Layer 4 - Vehicle State:** Hierarchical vehicle models with `VehicleState`

as base. `CarState`

implements Ackermann steering, `TruckState`

extends with trailer support (`TrailerState`

), and `CopterState`

models multicopters.

**Layer 5 - Sensors/Configuration:** GNSS receivers (`UbloxRover`

) with sensor fusion, camera control (`Gimbal`

), and centralized parameter management (`ParameterServer`

with MAVLink integration via `MavlinkParameterServer`

).

**Sources:** communication/mavsdkvehicleserver.h24-69 communication/vehicleconnections/vehicleconnection.h22-113 autopilot/purepursuitwaypointfollower.h41-126 vehicles/vehiclestate.h25-150

**Sources:** README.md6-12 communication/vehicleserver.h19-61 communication/vehicleconnections/vehicleconnection.h22-113

The vehicle-side application is built around `VehicleServer`

, which provides MAVLink server functionality and manages the autonomous vehicle's internal state and control loops.

**Key Classes:**

`MavsdkVehicleServer`

communication/mavsdkvehicleserver.h24-69 - Main vehicle-side server`VehicleState`

- Stores vehicle position, velocity, parameters`WaypointFollower`

- Implements autonomous route following`MovementController`

- Hardware-specific actuator control`GNSSReceiver`

- Positioning sensor interface**Sources:** communication/mavsdkvehicleserver.cpp15-482 communication/vehicleserver.h19-61

The desktop-side application uses `VehicleConnection`

to communicate with remote vehicles. It can optionally run a "connection-local" autopilot that computes control on the desktop and sends commands remotely.

**Key Pattern:** The `VehicleConnection`

class communication/vehicleconnections/vehicleconnection.cpp7-130 delegates autopilot commands either to:

**Sources:** communication/vehicleconnections/vehicleconnection.h22-115 communication/vehicleconnections/mavsdkvehicleconnection.cpp9-291

WayWise implements a three-tier architecture for vehicle communication:

**Tier 1 - Discovery:** `MavsdkStation`

discovers vehicles on the network and creates `VehicleConnection`

instances for each.

**Tier 2 - Abstraction:** `VehicleConnection`

provides a unified API and handles:

**Tier 3 - Protocol:** MAVSDK handles low-level MAVLink encoding/decoding and transport.

**Sources:** communication/mavsdkvehicleconnection.cpp9-37 communication/mavsdkvehicleserver.cpp23-42

**Key Message Handlers:**

`intercept_incoming_messages_async`

mavsdkvehicleserver.cpp147-292 - Intercepts incoming MAVLink messages`intercept_outgoing_messages_async`

mavsdkvehicleserver.cpp417-461 - Modifies outgoing messages`subscribe_flight_mode_change`

mavsdkvehicleserver.cpp83-106 - Handles mode changes from GCS**Sources:** communication/mavsdkvehicleserver.cpp147-461 communication/mavsdkvehicleconnection.cpp83-160

GNSS correction data (RTCM) is fragmented when exceeding MAVLink message size limits:

**Fragmentation Logic:** mavsdkvehicleconnection.cpp566-615

**Reassembly Logic:** mavsdkvehicleserver.cpp322-353

**Sources:** communication/mavsdkvehicleconnection.cpp566-615 communication/mavsdkvehicleserver.cpp322-353

All vehicle types inherit from `VehicleState`

or `ObjectState`

base classes:

**Title: Vehicle State Class Hierarchy**

**Multi-Source Position System:** Each `VehicleState`

maintains an array `mPositionBySource[(int)PosType::_LAST_]`

storing positions from different sources vehicles/vehiclestate.h134:

| PosType | Source | Usage |
|---|---|---|
`PosType::fused` | F9R ESF sensor fusion | Primary position for autopilot (GNSS + IMU + odometry) |
`PosType::GNSS` | Raw GNSS receiver | Fallback position, used when fusion unavailable |
`PosType::odom` | Wheel odometry | Dead-reckoning, used during GNSS outages |
`PosType::IMU` | Inertial sensors | High-rate updates |
`PosType::simulated` | Simulation | Testing without hardware |

The autopilot can select which position type to use via `setPosTypeUsed(PosType)`

autopilot/purepursuitwaypointfollower.h81 enabling flexible operation during sensor failures.

**Trailer System:** `TruckState`

extends `CarState`

with trailer support vehicles/truckstate.h13-58:

`mTrailerAngle_deg`

) received via MAVLink `NAMED_VALUE_FLOAT`

messages communication/mavsdkvehicleconnection.cpp368-377`getCurvatureWithTrailer()`

vehicles/truckstate.cpp84-107`updateTrailingVehicleOdomPositionAndYaw()`

vehicles/truckstate.cpp58-82**Sources:** vehicles/vehiclestate.h25-150 vehicles/carstate.h20-68 vehicles/truckstate.h13-58 vehicles/trailerstate.h19-54 vehicles/vehiclestate.cpp13-24 communication/mavsdkvehicleconnection.cpp368-377

The autopilot subsystem follows a strategy pattern with `WaypointFollower`

as the abstract interface:

**Title: Autopilot Architecture with Strategy Pattern**

**Dual-Mode Operation:** `PurepursuitWaypointFollower`

and `FollowPoint`

support both:

`MovementController`

autopilot/purepursuitwaypointfollower.cpp17-22`VehicleConnection`

commands autopilot/purepursuitwaypointfollower.cpp24-30Mode is determined by the constructor used and checked via `isOnVehicle()`

autopilot/purepursuitwaypointfollower.h49

**Pure Pursuit Implementation:** The `PurepursuitWaypointFollower`

implements a sophisticated path-following algorithm autopilot/purepursuitwaypointfollower.cpp1-649:

| Feature | Implementation | Purpose |
|---|---|---|
Look-ahead Radius | `purePursuitRadius()` purepursuitwaypointfollower.cpp479-492 | Distance ahead to find pursuit point |
Adaptive Radius | `mAdaptivePurePursuitRadiusCoefficient * speed` | Increases look-ahead at higher speeds |
State Machine | `WayPointFollowerSTMstates` enum purepursuitwaypointfollower.h20 | INIT → GOTO_BEGIN → FOLLOWING → APPROACHING_END_GOAL → FINISHED |
Speed Interpolation | `getInterpolatedSpeed()` purepursuitwaypointfollower.cpp459-467 | Smooth speed transitions between waypoints |
Trailer Support | `getVehicleReferencePosition()` purepursuitwaypointfollower.cpp51-60 | Uses trailer rear axle as reference when reversing |
End Goal Alignment | `getVehicleAlignmentReferencePosPoint()` purepursuitwaypointfollower.cpp504-529 | Precise alignment based on `AutopilotEndGoalAlignmentType` |
Speed Limit Zones | `mSpeedLimitRegions` purepursuitwaypointfollower.h108 | GeoJSON polygon-based speed restrictions |

**Trailer-Aware Path Following:** When a truck with trailer reverses (speed < 0), the autopilot:

`getCurvatureWithTrailer()`

for steering calculation vehicles/truckstate.cpp84-107**Sources:** autopilot/purepursuitwaypointfollower.h41-126 autopilot/purepursuitwaypointfollower.cpp1-649 vehicles/truckstate.cpp26-32 vehicles/truckstate.cpp84-107 communication/mavsdkvehicleserver.cpp83-106

Centralized parameter management with MAVLink synchronization:

**Registration Pattern:** Components register parameters with callbacks mavsdkvehicleserver.cpp484-490:

**Sources:** communication/mavsdkvehicleserver.cpp37-38 communication/mavsdkvehicleserver.cpp484-490

WayWise provides comprehensive support for truck-trailer combinations through specialized vehicle state modeling and autopilot integration.

**Title: Truck-Trailer System Integration**

**Component Discovery:** When `MavsdkVehicleConnection`

detects a truck (`WAYWISE_OBJECT_TYPE_TRUCK`

), it checks for trailer via `TRLR_COMP_ID`

parameter communication/mavsdkvehicleconnection.cpp328-381:

`TrailerState`

instance when component detected`NAMED_VALUE_FLOAT`

subscription for trailer yaw angle communication/mavsdkvehicleconnection.cpp368-377**Trailer Position Updates:** `TruckState::updateTrailingVehicleOdomPositionAndYaw()`

maintains trailer position vehicles/truckstate.cpp58-82:

`posInVehicleFrameToPosPointENU(getRearAxleToHitchOffset())`

`mRearAxleToHitchOffset`

`mSimulateTrailer = true`

**Trailer-Aware Steering:** `TruckState::getCurvatureWithTrailer()`

computes modified steering curvature vehicles/truckstate.cpp84-107:

| Mode | Calculation | Gain |
|---|---|---|
Forward | `atan(2 * l2 * sin(theta_err))` where `theta_err` is angle to target | `mPurePursuitForwardGain` (default: 1.0) |
Reverse | Accounts for trailer position in vehicle frame, uses autopilot radius | `mPurePursuitReverseGain` (default: -1.0) |

The curvature is divided by `cos(trailerAngle)`

to compensate for articulation geometry vehicles/truckstate.cpp106

**MAVLink Trailer Component:** `MavsdkVehicleServer::createMavsdkComponentForTrailer()`

creates a separate MAVLink component for the trailer communication/mavsdkvehicleserver.cpp759-826:

`NAMED_VALUE_FLOAT`

with name "TRLR_YAW" communication/mavsdkvehicleserver.cpp791-807`MAV_TYPE_GENERIC`

communication/mavsdkvehicleserver.cpp793**Sources:** vehicles/truckstate.h13-58 vehicles/truckstate.cpp26-32 vehicles/truckstate.cpp58-82 vehicles/truckstate.cpp84-107 vehicles/trailerstate.h19-54 communication/mavsdkvehicleconnection.cpp319-382 communication/mavsdkvehicleserver.cpp759-826

Both vehicle and desktop sides implement a **2-second heartbeat timeout** that triggers emergency stop:

**Title: Heartbeat Safety Protocol**

**Vehicle-Side Implementation:** `MavsdkVehicleServer`

monitors heartbeats communication/mavsdkvehicleserver.cpp141-153:

`HEARTBEAT`

messages with `intercept_incoming_messages_async()`

`resetHeartbeat()`

signal to restart timer`heartbeatTimeout()`

stops autopilot and zeros actuators communication/mavsdkvehicleserver.cpp492-504**Desktop-Side Implementation:** `MavsdkStation`

tracks vehicle connections communication/mavsdkvehicleconnections/mavsdkstation.cpp70-92:

`mVehicleHeartbeatTimeoutCounters`

vector with 5-second timeout communication/mavsdkstation.h51-52`mVehicleConnectionMap`

`disconnectOfVehicleConnection`

signal for UI updates**Timeout Constants:**

`mCountdown_ms = 2000`

ms communication/vehicleserver.h55`HEARTBEATTIMER_TIMEOUT_SECONDS = 5`

seconds communication/mavsdkstation.h51**Sources:** communication/mavsdkvehicleserver.cpp141-153 communication/mavsdkvehicleserver.cpp492-510 communication/vehicleserver.h53-58 communication/mavsdkstation.cpp70-92 communication/mavsdkstation.h51-52

The autopilot can receive emergency brake signals from sensor fusion:

**Title: Emergency Brake System**

The `WaypointFollower`

connects to `EmergencyBrake::emergencyBrake`

signal and emits `activateEmergencyBrake()`

/`deactivateEmergencyBrake()`

signals for the brake system to use.

**Sources:** autopilot/purepursuitwaypointfollower.cpp127-173

WayWise uses three coordinate systems with transformations between them:

| Frame | Description | Usage |
|---|---|---|
LLH | Latitude/Longitude/Height (WGS84) | Global GNSS coordinates, human-readable |
NED | North-East-Down | Vehicle EKF on PX4 drones, MAVLink standard |
ENU | East-North-Up | Internal WayWise coordinate system |

**Key Transformations:**

`yawNEDtoENU()`

and `yawENUtoNED()`

mavsdkvehicleconnection.cpp129-135**ENU Reference Setup:**

`GPS_GLOBAL_ORIGIN`

message`sendGpsOriginLlh()`

mavsdkvehicleserver.cpp66-75**Sources:** communication/mavsdkvehicleconnection.cpp95-141 communication/mavsdkvehicleserver.cpp50-80

Refresh this wiki
