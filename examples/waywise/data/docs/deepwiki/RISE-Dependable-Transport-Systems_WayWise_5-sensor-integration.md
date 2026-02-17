# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/5-sensor-integration

The sensor integration layer in WayWise bridges hardware sensors with the vehicle state management system, providing position data, orientation information, and environmental awareness for autonomous vehicle operations. This page provides an overview of the sensor architecture and integration patterns used throughout the system.

For detailed documentation of specific sensor implementations, see:

WayWise uses a modular sensor architecture where different sensor types inherit from abstract base classes and provide position data through standardized interfaces. The sensor layer is independent of the vehicle state management, allowing flexible sensor configurations.

**Diagram: Sensor Class Hierarchy and Integration**

Sources: sensors/gnss/gnssreceiver.h44-84 sensors/gnss/ubloxrover.h19-69 sensors/gnss/ublox.h608-861 sensors/camera/gimbal.h11-27 sensors/camera/mavsdkgimbal.h14-30

**Diagram: Sensor Data Flow from Hardware to Vehicle State**

Sources: sensors/gnss/ubloxrover.cpp15-20 sensors/gnss/ubloxrover.cpp343-414 sensors/camera/mavsdkgimbal.cpp8-21 sensors/camera/mavsdkgimbal.cpp24-46

The `GNSSReceiver`

abstract base class sensors/gnss/gnssreceiver.h44-84 defines the interface for all GNSS sensor implementations. It manages ENU reference frames, coordinate offsets, and receiver state transitions.

| Method | Purpose |
|---|---|
`setEnuRef(llh_t)` | Set the local ENU coordinate reference point |
`setChipOrientationOffset()` | Configure IMU/receiver mounting angles |
`setAntennaToChipOffset()` | Set lever arm from antenna to IMU |
`setChipToRearAxleOffset()` | Set lever arm from IMU to rear axle |
`aboutToShutdown()` | Graceful shutdown handling |
`readVehicleSpeedForPositionFusion()` | Provide odometry for sensor fusion |

**Diagram: GNSS Receiver State Machine (RECEIVER_STATE enum)**

The receiver state machine is particularly important for the ZED-F9R variant, which requires sensor calibration before External Sensor Fusion (ESF) can be enabled. See 5.1 GNSS Receivers for detailed state transitions and configuration.

Sources: sensors/gnss/gnssreceiver.h21-33 sensors/gnss/ubloxrover.cpp45-79 sensors/gnss/ubloxrover.cpp546-580

WayWise uses a `PosType`

enumeration to distinguish position data from different sensor sources. Each `PosPoint`

stores its position type, allowing the system to:

`TraceModule`

)| PosType | Source | Description | Primary Use Case |
|---|---|---|---|
`simulated` | Software | Virtual position data | Testing and simulation |
`GNSS` | GNSS receivers | Raw GNSS position (no fusion) | ZED-F9P receivers |
`fused` | Sensor fusion | IMU + GNSS + odometry | ZED-F9R with ESF enabled |
`IMU` | Inertial sensors | Dead reckoning | GNSS-denied navigation |
`odometry` | Wheel encoders | Integrated wheel speed | Short-term position updates |
`UWB` | Ultra-wideband | Indoor positioning | Indoor localization |

The `PosType`

is set when calling `VehicleState::setPosition(PosPoint)`

. For u-blox receivers:

`PosType::GNSS`

(no fusion available)`PosType::fused`

when ESF is calibrated and enabledSources: core/pospoint.h1-50 sensors/gnss/ubloxrover.cpp353-401

The GNSS subsystem provides the primary positioning capability for outdoor vehicle operations. WayWise has deep integration with u-blox ZED-F9P and ZED-F9R receivers, supporting:

| Class | File | Purpose |
|---|---|---|
`GNSSReceiver` | sensors/gnss/gnssreceiver.h44-84 | Abstract base class |
`UbloxRover` | sensors/gnss/ubloxrover.h19-69 | u-blox rover implementation |
`Ublox` | sensors/gnss/ublox.h608-861 | UBX protocol handler and serial communication |

**Diagram: GNSS Receiver Configuration Flow**

For detailed documentation of GNSS configuration, RTK setup, ESF sensor fusion, and receiver state management, see 5.1 GNSS Receivers.

Sources: sensors/gnss/ubloxrover.cpp196-214 sensors/gnss/ubloxrover.cpp252-341 sensors/gnss/ubloxrover.cpp416-473

The map visualization system provides real-time display of sensor data and vehicle positions. The `MapWidget`

serves as the primary visualization component, integrating data from multiple sensor sources.

The `TraceModule`

enables visualization of position traces from different sensor types, allowing operators to compare the performance and accuracy of various positioning sources:

Sources: userinterface/map/tracemodule.cpp7-36 userinterface/map/tracemodule.h32-43

The sensor integration system uses a comprehensive coordinate transformation framework to handle different reference frames and coordinate systems used by various sensors.

The system establishes an East-North-Up (ENU) reference frame for local coordinate operations:

`{57.71495867, 12.89134921, 219.0}`

Sources: userinterface/map/mapwidget.cpp42-43 userinterface/map/mapwidget.cpp517-533

The sensor integration system provides comprehensive status monitoring and quality assessment for all connected sensors:

The sensor data flows into the vehicle state management system through well-defined interfaces:

`VehicleState::setPosition()`

Sources: sensors/gnss/ublox.h94-164 userinterface/map/mapwidget.cpp57-61

Refresh this wiki
