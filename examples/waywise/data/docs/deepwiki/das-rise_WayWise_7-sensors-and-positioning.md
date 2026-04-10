# Source: https://deepwiki.com/das-rise/WayWise/7-sensors-and-positioning

This page provides a high-level overview of the sensor subsystems and positioning logic within the WayWise framework. The system is designed to handle multiple sources of spatial data—GNSS, IMU, Odometry, UWB, and Computer Vision—fusing them to provide a stable and accurate `fused`

position for autopilot and navigation.

The sensing layer is built around the `ObjectState`

and `VehicleState`

classes, which act as the central data hub. Sensors are implemented as "Updaters" or "Receivers" that populate specific `PosType`

slots (e.g., `PosType::GNSS`

, `PosType::IMU`

, `PosType::odom`

) within the state object. A dedicated fusion module then reconciles these inputs.

The following diagram illustrates how physical sensor categories map to their respective C++ implementation classes and their interaction with the vehicle state.

**Sensor Subsystem Mapping**

Sources: sensors/gnss/ubloxrover.h19-20 sensors/gnss/gnssreceiver.h21-28

The GNSS subsystem focuses on high-precision positioning using u-blox ZED-F9P (RTK) and ZED-F9R (Sensor Fusion) modules. The `GNSSReceiver`

base class handles the conversion from Geodetic coordinates (LLH) to the local Cartesian East-North-Up (ENU) frame used by the autopilot sensors/gnss/gnssreceiver.cpp69-72

Key features include:

`NAV-PVT`

(Position/Velocity/Time) and `ESF`

(External Sensor Fusion) messages sensors/gnss/ubloxrover.cpp15-20`RtcmClient`

connects to NTRIP casters to stream RTCM correction data, which is then injected into the u-blox chip via `writeRtcmToUblox`

sensors/gnss/rtcmclient.cpp10-15 sensors/gnss/ubloxrover.h26For details, see GNSS: u-blox Receiver & RTK.

The `SDVPVehiclePositionFuser`

is responsible for generating the `fused`

position used for navigation. It addresses the latency and low frequency of GNSS updates by using a history buffer sensors/fusion/sdvpvehiclepositionfuser.h14-17

**Fusion Logic Flow**

The fuser supports two primary modes:

For details, see Sensor Fusion: SDVP Position Fuser.

Beyond primary positioning, WayWise supports a variety of auxiliary sensors for orientation and environmental awareness:

For details, see IMU, Angle, UWB & ToF Sensors.

WayWise integrates with DepthAI (OAK-D) cameras for advanced spatial sensing. The `DepthAiCamera`

class parses JSON streams over TCP, providing:

`MavsdkGimbal`

to orient the camera sensors during flight or driving tasks.For details, see Camera & Object Detection.

| Data Type | Code Entity | Source | Primary Use |
|---|---|---|---|
LLH/ENU | `llh_t` , `xyz_t` | `GNSSReceiver` | Global/Local Position |
Orientation | `rpy_t` | `IMUOrientationUpdater` | Heading & Attitude |
RTK Corrections | `QByteArray` | `RtcmClient` | Centimeter accuracy |
Odometry | `drivenDistance` | `VescMotorController` | Dead Reckoning |

Sources: sensors/gnss/gnssreceiver.h53-62 sensors/gnss/ublox.h148-165 sensors/fusion/sdvpvehiclepositionfuser.h45-49

Refresh this wiki

This wiki was recently refreshed. Please wait 6 days to refresh again.