# Source: https://deepwiki.com/das-rise/WayWise/7.2-sensor-fusion:-sdvp-position-fuser

The `SDVPVehiclePositionFuser`

class implements a sensor fusion algorithm designed to provide a continuous, high-frequency estimate of a vehicle's position and orientation. It addresses the inherent limitations of individual sensors: GNSS provides absolute accuracy but suffers from high latency and low update rates; IMUs provide high-frequency data but are subject to orientation drift; and odometry provides smooth relative movement but accumulates error over time sensors/fusion/sdvpvehiclepositionfuser.h5-17

The fuser operates in two primary modes depending on the hardware capabilities of the connected GNSS receiver (typically a u-blox ZED-F9R or F9P) sensors/fusion/sdvpvehiclepositionfuser.h57

When using a receiver like the **u-blox ZED-F9R**, sensor fusion (GNSS + IMU + Wheel Ticks) is performed directly on the u-blox chip sensors/gnss/ubloxrover.cpp52-56

`mFusionOnChip`

flag sensors/fusion/sdvpvehiclepositionfuser.cpp65When on-chip fusion is unavailable or disabled, `SDVPVehiclePositionFuser`

performs software-based fusion using a history-buffered latency compensation approach sensors/fusion/sdvpvehiclepositionfuser.h9-17

| Feature | Implementation Detail |
|---|---|
Latency Compensation | Uses a circular history buffer of size 128 to store previous fused states sensors/fusion/sdvpvehiclepositionfuser.h64-66 |
Yaw Correction | Corrects IMU-based yaw using GNSS heading, reversing logic if the vehicle is moving backwards sensors/fusion/sdvpvehiclepositionfuser.cpp79-84 |
Position Correction | Applies weighted updates to the current position based on GNSS errors calculated at the historical timestamp sensors/fusion/sdvpvehiclepositionfuser.cpp90-101 |
Standstill Handling | Freezes yaw during standstill to prevent IMU drift from affecting the fused heading sensors/fusion/sdvpvehiclepositionfuser.cpp141-153 |

**Sources:** sensors/fusion/sdvpvehiclepositionfuser.h5-17 sensors/fusion/sdvpvehiclepositionfuser.cpp65-72 sensors/gnss/ubloxrover.cpp52-56

The following diagram illustrates how the `SDVPVehiclePositionFuser`

interacts with the `ObjectState`

and various sensor inputs.

**Sources:** sensors/fusion/sdvpvehiclepositionfuser.cpp63 sensors/fusion/sdvpvehiclepositionfuser.cpp110 sensors/fusion/sdvpvehiclepositionfuser.cpp129 sensors/fusion/sdvpvehiclepositionfuser.h45-54 sensors/gnss/gnssreceiver.cpp59-60

Because GNSS measurements represent where the vehicle was in the past (due to processing and transmission delays), the fuser maintains a `mPosFusedHistory`

sensors/fusion/sdvpvehiclepositionfuser.h65

`getClosestPosFusedSampleInTime(posGNSS.getTime())`

sensors/fusion/sdvpvehiclepositionfuser.cpp75The fuser uses several parameters to control how aggressively it trusts GNSS data:

`mPosGNSSxyStaticGain`

`mPosGNSSxyDynamicGain`

`mPosGNSSyawGain`

If the distance between the GNSS position and the fused estimate exceeds `BIG_DISTANCE_ERROR_m`

(50.0 meters), the fuser "jumps" the fused position directly to the GNSS coordinate to recover from significant tracking loss sensors/fusion/sdvpvehiclepositionfuser.cpp95-98

To combat IMU gyro drift while the vehicle is stationary:

`objectState->getSpeed()`

sensors/fusion/sdvpvehiclepositionfuser.cpp141`yawWhenStopping`

sensors/fusion/sdvpvehiclepositionfuser.cpp143`yawDriftSinceStandstill`

and forces the IMU yaw to the stopped value sensors/fusion/sdvpvehiclepositionfuser.cpp146-147`mPosIMUyawOffset`

sensors/fusion/sdvpvehiclepositionfuser.cpp150**Sources:** sensors/fusion/sdvpvehiclepositionfuser.cpp75-101 sensors/fusion/sdvpvehiclepositionfuser.cpp141-153 sensors/fusion/sdvpvehiclepositionfuser.h58-62

The `UbloxRover`

class manages the state of the physical receiver and provides the necessary inputs for the fuser.

The `UbloxRover`

monitors the `ubx_esf_status`

message to determine the calibration state of the hardware sensors sensors/gnss/ubloxrover.cpp44-45

| State | Condition |
|---|---|
`CALIBRATING` | `fusion_mode == 0` (Hardware sensors initializing) sensors/gnss/ubloxrover.cpp49-51 |
`READY` | `fusion_mode == 1` (Hardware fusion active and calibrated) sensors/gnss/ubloxrover.cpp52-54 |

The `GNSSReceiver`

base class (and thus `UbloxRover`

) handles transformations from the GNSS antenna/chip to the vehicle's rear axle (the "base" frame) sensors/gnss/gnssreceiver.h74-76

`mAntennaToChipOffset`

: Physical distance between antenna and the IMU chip sensors/gnss/gnssreceiver.h92`mChipToBaseOffset`

: Distance from the IMU chip to the vehicle's center of rotation sensors/gnss/gnssreceiver.h93`updateGNSSPositionAndOrientation`

applies these offsets using the current fused yaw to ensure the `PosType::GNSS`

stored in `ObjectState`

refers to the vehicle's reference point, not the antenna's location sensors/gnss/gnssreceiver.cpp86-102**Sources:** sensors/gnss/ubloxrover.cpp15-20 sensors/gnss/gnssreceiver.cpp59-104 sensors/fusion/sdvpvehiclepositionfuser.cpp63-73

Refresh this wiki

This wiki was recently refreshed. Please wait 6 days to refresh again.