# Source: https://deepwiki.com/das-rise/WayWise/6-communication-layer

The WayWise Communication Layer provides a multi-protocol interface for vehicle-to-station and vehicle-to-vehicle interaction. It abstractly handles telemetry streaming, mission management, parameter synchronization, and manual control overrides. The architecture is split between **Server** components (running on the vehicle) and **Connection/Station** components (running on the ground station or control tower).

The system primarily utilizes MAVLink via the MAVSDK library for standard operations, but maintains a modular structure to support ISO 22133 and legacy TCP protocols.

**High-Level Entity Relationship**

**Sources:** communication/vehicleserver.h19-61 communication/vehicleconnections/vehicleconnection.h22-113 communication/mavsdkvehicleserver.h24-71

The `MavsdkVehicleServer`

acts as the primary MAVLink interface on the vehicle. It instantiates a MAVSDK `Autopilot`

component communication/mavsdkvehicleserver.cpp22-25 and manages several MAVSDK server plugins:

`PosPoint`

objects for the `WaypointFollower`

communication/mavsdkvehicleserver.cpp105-121For details, see MAVLink Vehicle Server (On-Vehicle Side).

**Sources:** communication/mavsdkvehicleserver.cpp15-141 communication/mavsdkvehicleserver.h24-71

The ground station side is managed by `MavsdkStation`

(for discovery) and `MavsdkVehicleConnection`

. The connection class wraps MAVSDK plugins to provide a high-level API for the UI.

`HEARTBEAT`

and `VEH_WW_OBJ_TYPE`

parameters communication/vehicleconnections/mavsdkvehicleconnection.cpp18-66`WaypointFollower`

, allowing the ground station to calculate steering commands and send them as raw velocity/yaw targets if the vehicle lacks an onboard autopilot communication/vehicleconnections/vehicleconnection.cpp7-23For details, see MAVLink Vehicle Connection & Station (Ground-Station Side).

**Sources:** communication/vehicleconnections/mavsdkvehicleconnection.cpp9-155 communication/vehicleconnections/vehicleconnection.h70-86

The `iso22133VehicleServer`

provides compatibility with the ISO 22133 standard for automated vehicle operations. It handles specific message types like `OSEM`

(Operational Status), `TRAJ`

(Trajectory), and `MONR`

(Monitoring). This server translates ISO 22133 trajectories into `PosPoint`

lists for the internal `PurepursuitWaypointFollower`

.

For details, see ISO 22133 Vehicle Server.

The `ParameterServer`

is a singleton that manages vehicle configuration. It uses a "provider" pattern where various subsystems (like `PurepursuitWaypointFollower`

) register their variables via functional bindings autopilot/purepursuitwaypointfollower.cpp31-37

`ParameterServer`

to the MAVLink `PARAM`

protocol, allowing standard GCS tools (like QGroundControl) to edit WayWise-specific parameters communication/mavlinkparameterserver.cpp37-49For details, see Parameter Server.

**Sources:** communication/parameterserver.h14-52 communication/mavlinkparameterserver.h11-30

This subsystem supports older binary protocols and specialized data streams:

`MavsdkVehicleConnection::inputRtcmData`

communication/vehicleconnections/mavsdkvehicleconnection.cpp52For details, see Legacy & TCP Communication.

The following diagram illustrates how a mission command moves from the Ground Station UI to the Vehicle Actuators.

**Sources:** communication/vehicleconnections/vehicleconnection.cpp75-82 communication/mavsdkvehicleserver.cpp105-121 autopilot/purepursuitwaypointfollower.cpp88-116 autopilot/purepursuitwaypointfollower.h115

Refresh this wiki

This wiki was recently refreshed. Please wait 7 days to refresh again.