# Source: https://deepwiki.com/das-rise/WayWise/7.1-gnss:-u-blox-receiver-and-rtk

This section details the GNSS subsystem, focusing on the integration of u-blox ZED-F9P and ZED-F9R receivers, RTK (Real-Time Kinematic) correction handling via NTRIP, and the base station configuration.

The `GNSSReceiver`

class serves as the abstract foundation for all GNSS implementations. It provides the logic for converting raw Geographic coordinates (Latitude, Longitude, Height - LLH) into the local Cartesian system (East, North, Up - ENU) used by the vehicle's `ObjectState`

sensors/gnss/gnssreceiver.h64-68

`ObjectState`

sensors/gnss/gnssreceiver.cpp65-70`simulationStep`

function that mimics GNSS updates based on odometry data, allowing for software-in-the-loop testing without hardware sensors/gnss/gnssreceiver.cpp15-57The following diagram illustrates how raw LLH data is processed through the base class into the vehicle state.

**Diagram: GNSS Data Transformation Flow**

Sources: sensors/gnss/gnssreceiver.cpp59-104 sensors/gnss/gnssreceiver.h80-84

The `UbloxRover`

class implements the serial driver for u-blox F9-series receivers. It handles the binary **UBX protocol** and manages receiver-specific states such as calibration and configuration sensors/gnss/ubloxrover.h19-23

`NAV-PVT`

(Position, Velocity, Time), `NAV-STATUS`

, and `NAV-RELPOSNED`

(for moving base/heading) sensors/gnss/ublox.cpp192-226`ESF-STATUS`

and `ESF-ALG`

messages. It monitors the `fusion_mode`

to transition the receiver state between `CALIBRATING`

and `READY`

sensors/gnss/ubloxrover.cpp44-79`UPD-SOS`

to save the current GNSS/IMU calibration to flash memory upon shutdown and restores it on startup to minimize calibration time sensors/gnss/ubloxrover.cpp67-68 sensors/gnss/ubloxrover.h48-49`writeRtcmToUblox`

to forward correction data from an NTRIP client directly to the receiver hardware sensors/gnss/ubloxrover.cpp152-155The `UbloxRover`

tracks the hardware status using the `RECEIVER_STATE`

enum:

`fusion_mode == 0`

) sensors/gnss/ubloxrover.cpp49-51`fusion_mode == 1`

) sensors/gnss/ubloxrover.cpp52-54Sources: sensors/gnss/ubloxrover.cpp11-111 sensors/gnss/ublox.h148-182 sensors/gnss/gnssreceiver.h30-42

The `RtcmClient`

manages the connection to an NTRIP (Networked Transport of RTCM via Internet Protocol) caster to receive RTK corrections sensors/gnss/rtcmclient.h31-35

`RtcmClient::forwardNmeaGgaToServer`

sends NMEA GGA strings back to the server sensors/gnss/rtcmclient.cpp163-169`0xD3`

). Specifically, it decodes types `1005`

or `1006`

to extract the Base Station's LLH position sensors/gnss/rtcmclient.cpp48-68**Diagram: RTK Correction Pipeline**

Sources: sensors/gnss/rtcmclient.cpp10-71 sensors/gnss/ubloxrover.cpp152-155 sensors/gnss/rtcmclient.h45-49

For deployments without a public NTRIP caster, the `ublox_basestation`

module allows a WayWise-connected u-blox receiver to act as a local RTK base sensors/gnss/ublox_basestation.h16-20

`ubx_nav_svin`

message reports `valid`

, the receiver begins outputting RTCM messages sensors/gnss/ublox.h42-52The base station logic manages the `VALSET`

configuration keys required to enable specific RTCM3 messages (e.g., 1005, 1077, 1087, 1097, 1127) on the serial port sensors/gnss/ublox.cpp270-280

Sources: sensors/gnss/ublox_basestation.cpp10-50 sensors/gnss/ublox.h42-52

While `UbloxRover`

handles on-chip fusion (F9R), WayWise also supports off-chip fusion via `SDVPVehiclePositionFuser`

.

`mPosFusedHistory`

buffer to match old GNSS timestamps with higher-frequency IMU/Odometry samples sensors/fusion/sdvpvehiclepositionfuser.cpp13-39`mPosGNSSxyDynamicGain`

) to smoothly transition the vehicle's "fused" position toward the "ground truth" provided by GNSS sensors/fusion/sdvpvehiclepositionfuser.cpp88-102Sources: sensors/fusion/sdvpvehiclepositionfuser.h27-67 sensors/fusion/sdvpvehiclepositionfuser.cpp63-108

Refresh this wiki

This wiki was recently refreshed. Please wait 6 days to refresh again.