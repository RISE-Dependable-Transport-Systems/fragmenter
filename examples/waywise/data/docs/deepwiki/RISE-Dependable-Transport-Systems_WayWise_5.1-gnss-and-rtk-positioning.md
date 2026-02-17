# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/5.1-gnss-and-rtk-positioning

This document describes the `UbloxRover`

implementation for u-blox ZED-F9P and ZED-F9R GNSS receivers in WayWise. These receivers provide centimeter-level positioning accuracy through RTK (Real-Time Kinematic) corrections. The ZED-F9R additionally provides advanced sensor fusion with internal IMU and external odometry data.

`UbloxRover`

handles:

Related documentation: See State Architecture & PosPoint for how GNSS positions integrate with vehicle state, and Camera & Gimbal Control for other sensors.

**Sources:** sensors/gnss/ubloxrover.h sensors/gnss/ubloxrover.cpp sensors/gnss/gnssreceiver.h

**Key Components:**

| Class | Responsibility |
|---|---|
`GNSSReceiver` | Abstract base defining the interface for all GNSS receivers |
`UbloxRover` | Implements rover-side configuration, calibration state machine, and position updates |
`UbloxBasestation` | Configures a static receiver to generate RTCM correction messages |
`Ublox` | Low-level protocol handler for UBX and RTCM message encoding/decoding |
`VehicleState` | Stores multiple position sources including GNSS, fused, and odometry |

**Sources:** sensors/gnss/gnssreceiver.h44-74 sensors/gnss/ubloxrover.h19-68 sensors/gnss/ublox_basestation.h18-58 sensors/gnss/ublox.h608-700

WayWise supports two u-blox receiver models with distinct capabilities:

`PosType::GNSS`

) and fused (`PosType::fused`

)The receiver variant is determined during initialization and controls which configuration path is taken.

**Sources:** sensors/gnss/gnssreceiver.h19 sensors/gnss/ubloxrover.cpp16-19 sensors/gnss/ubloxrover.cpp326-337

| State | Description | Entry Conditions |
|---|---|---|
`DISCONNECTED` | Serial port not connected | Initial state or after shutdown |
`CONNECTED` | Serial communication established | `connectSerial()` succeeds |
`BACKUP_RESTORED` | Previous calibration restored from flash | UBX-UPD-SOS response = 2 |
`BACKUP_NOT_FOUND` | No saved calibration found | UBX-UPD-SOS response = 3 |
`CONFIGURED` | UBX messages configured, awaiting sensor status | After `configureUblox()` |
`CALIBRATING` | F9R sensors calibrating during motion | ESF-STATUS fusion_mode = 0 |
`READY` | Receiver operational, full accuracy available | F9P: immediate; F9R: fusion_mode = 1 |
`BACKUP_ONGOING` | Creating flash backup of calibration | During shutdown sequence |
`BACKUP_CREATED` | Backup successfully written | After UBX-UPD-SOS backup ACK |

**Sources:** sensors/gnss/gnssreceiver.h21-33 sensors/gnss/ubloxrover.cpp196-213 sensors/gnss/ubloxrover.cpp416-473 sensors/gnss/ubloxrover.cpp44-79

The configuration sequence differs based on receiver variant and whether a backup exists:

**GNSS Constellations:**

**F9R-Specific ESF Configuration:**

| Parameter | Configuration Key | Description |
|---|---|---|
| Sensor Fusion Enable | `CFG_SFCORE_USE_SF` | Enables IMU/odometry fusion |
| Speed Input | `CFG_SFODO_USE_SPEED` | Use mm/s speed data from vehicle |
| Speed Frequency | `CFG_SFODO_FREQUENCY` | Expected odometry update rate (Hz) |
| Quantization Error | `CFG_SFODO_QUANT_ERROR` | Speed data accuracy (1e-6 units) |
| IMU-Antenna Offset | `CFG_SFIMU_IMU2ANT_LA_{X,Y,Z}` | Physical antenna position (cm) |
| IMU-VRP Offset | `CFG_SFODO_IMU2VRP_LA_{X,Y,Z}` | Vehicle reference point position (cm) |
| Auto Mount Alignment | `ubloxCfgAppendMntalg()` | Enable/configure automatic orientation |

**Sources:** sensors/gnss/ubloxrover.cpp252-341 sensors/gnss/ublox.cpp796-878

The F9R requires an initialization phase where it:

**Calibration Requirements:**

`readVehicleSpeedForPositionFusion()`

When `mESFAlgAutoMntAlgOn = true`

, the receiver continuously updates orientation offsets:

These offsets are applied during position updates to correct the heading:

**Sources:** sensors/gnss/ubloxrover.cpp231-248 sensors/gnss/ubloxrover.cpp26-39 sensors/gnss/ubloxrover.cpp267-319 sensors/gnss/ubloxrover.cpp368-379

RTK positioning requires differential correction data from a base station. The rover receives RTCM3 messages and forwards them to the u-blox receiver:

**RTK Fix Types:**
The quality of RTK correction is indicated by the `carr_soln`

field in UBX-NAV-PVT:

| Value | Fix Type | Typical Accuracy |
|---|---|---|
| 0 | No RTK | 1-5m (standalone GNSS) |
| 1 | RTK Float | 0.1-0.5m |
| 2 | RTK Fixed | 0.01-0.02m (horizontal) |

**RTCM Message Support:**
`UbloxRover`

accepts raw RTCM3 byte streams via `writeRtcmToUblox()`

. The receiver automatically decodes:

**Sources:** sensors/gnss/ubloxrover.h26 sensors/gnss/ubloxrover.cpp221-224 sensors/gnss/ublox.h116 communication/vehicleserver/mavsdkvehicleserver.cpp

The rover maintains multiple position estimates simultaneously in `VehicleState`

:

| PosType | Source | Available On | Accuracy |
|---|---|---|---|
`PosType::GNSS` | Raw satellite positioning | F9P, F9R | 1-5m (no RTK) 0.01-0.02m (with RTK) |
`PosType::fused` | ESF sensor fusion | F9R only | 0.01-0.1m (includes IMU drift compensation) |
`PosType::odom` | Dead reckoning from wheels | F9R only | Degrades over time without GNSS |

Physical sensors are not located at the vehicle reference point (typically rear axle center). Three offset corrections are applied:

**Application During Position Update:**

For F9R (heading from receiver):

For F9P (heading from separate source):

**Configuration:**
Offsets are set via `GNSSReceiver`

interface and stored in the base class:

**Sources:** sensors/gnss/ubloxrover.cpp343-414 sensors/gnss/gnssreceiver.h52-54 sensors/gnss/gnssreceiver.h70-72

The `Ublox`

class implements a state machine decoder for UBX protocol messages:

| Message Class.ID | Name | Purpose | Handler Signal |
|---|---|---|---|
`NAV.PVT (0x01 0x07)` | Navigation Position Velocity Time | Primary position/velocity output | `rxNavPvt()` |
`ESF.STATUS (0x10 0x10)` | External Sensor Fusion status | Calibration state, sensor health | `rxEsfStatus()` |
`ESF.ALG (0x10 0x14)` | ESF Alignment angles | IMU mount orientation | `rxEsfAlg()` |
`ESF.MEAS (0x10 0x02)` | ESF Measurements | Sensor data input | `rxEsfMeas()` |
`CFG.VALSET (0x06 0x8A)` | Configuration value set | Apply configuration keys | (command only) |
`UPD.SOS (0x09 0x14)` | Backup/restore operations | Save/load calibration | `rxUpdSos()` |
`RTCM3 (0xF5)` | RTCM corrections | Differential corrections | `rtcmRx()` |

Modern u-blox receivers use a key-value configuration system accessed via `UBX-CFG-VALSET`

:

**Configuration Layers:**

**Sources:** sensors/gnss/ublox.cpp192-226 sensors/gnss/ublox.cpp713-739 sensors/gnss/ublox.h18-210

The F9R can save/restore ESF calibration data to/from internal flash memory, avoiding recalibration on subsequent startups:

Backup is created only when:

`READY`

state (fully calibrated)`mCreateBackupWithSoS`

flag is set`aboutToShutdown()`

**Note:** The receiver must be power-cycled for the backup to be detected on next startup. The code issues a controlled GNSS restart, but the documentation recommends a full power cycle.

**Sources:** sensors/gnss/ubloxrover.cpp416-473 sensors/gnss/ubloxrover.cpp475-521 sensors/gnss/ubloxrover.cpp546-580

The first valid GNSS position establishes the local East-North-Up (ENU) coordinate origin:

Subsequent positions are transformed from geodetic coordinates (latitude, longitude, height) to local Cartesian ENU coordinates:

**Coordinate Frames:**

| Frame | Description | Usage |
|---|---|---|
LLH | Latitude, Longitude, Height (WGS84) | Raw GNSS output, global reference |
ENU | East, North, Up (local Cartesian) | Planning, control, visualization |
NED | North, East, Down | Heading output from receiver |

**Heading Transformation:**
The ZED-F9R outputs heading in NED frame, which is converted to ENU:

This creates a consistent ENU coordinate system for all vehicle operations, where:

**Sources:** sensors/gnss/ubloxrover.cpp358-363 sensors/gnss/ubloxrover.cpp369-379 core/coordinatetransforms.h core/coordinatetransforms.cpp

The `UBX-ESF-STATUS`

message provides detailed sensor health information:

Position accuracy estimates are updated with every NAV-PVT message:

These values indicate:

**Sources:** sensors/gnss/ubloxrover.cpp44-111 sensors/gnss/ubloxrover.cpp404-407 sensors/gnss/gnssreceiver.h37-42

Refresh this wiki
