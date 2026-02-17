# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/5.2-sensor-fusion-algorithm

This page documents the **SDVPVehiclePositionFuser** sensor fusion algorithm that combines GNSS, IMU, and odometry data to produce accurate, low-latency vehicle position and orientation estimates. The algorithm addresses two fundamental challenges: GNSS position data is accurate but delayed (typically 200-500ms old), while IMU orientation is fast but drifts over time.

For information about GNSS receiver configuration and RTK positioning, see GNSS & RTK Positioning. For camera and gimbal sensor integration, see Camera & Gimbal Control.

**Sources:** sensors/fusion/sdvpvehiclepositionfuser.h1-70 sensors/fusion/sdvpvehiclepositionfuser.cpp1-178

The sensor fusion system operates in two modes depending on the GNSS receiver hardware:

| Mode | Receiver | Fusion Location | Description |
|---|---|---|---|
On-Chip Fusion | u-blox ZED-F9R | Inside receiver | Receiver performs sensor fusion internally using its IMU, odometry inputs, and GNSS |
External Fusion | u-blox ZED-F9P | SDVPVehiclePositionFuser | WayWise performs fusion algorithm in software |

The external fusion algorithm is a rewritten and restructured version of SDVP's position estimation system, designed specifically to handle the temporal mismatch between sensor update rates.

**Sources:** sensors/fusion/sdvpvehiclepositionfuser.h5-16 sensors/gnss/ubloxrover.cpp49-76

**Sources:** sensors/fusion/sdvpvehiclepositionfuser.cpp63-107 sensors/gnss/ubloxrover.cpp15-20 vehicles/vehiclestate.h

The external fusion algorithm implements a time-synchronized correction approach with three key insights:

**GNSS Latency Compensation**: When GNSS data arrives with timestamp T-300ms, the algorithm retrieves the fused position at T-300ms from history, calculates the error, and applies a weighted correction to the current position at T.

**IMU Drift Correction**: The algorithm maintains a yaw offset (`mPosIMUyawOffset`

) that is continuously adjusted based on GNSS heading. At standstill, IMU drift is tracked and compensated.

**Odometry Dead Reckoning**: Between GNSS updates, odometry distance is used with the current fused yaw to predict position changes.

**Sources:** sensors/fusion/sdvpvehiclepositionfuser.h8-16

The algorithm maintains a circular buffer of 128 samples:

| Parameter | Value | Description |
|---|---|---|
`POSFUSED_HISTORY_SIZE` | 128 | Number of historical samples |
`mPosFusedHistory` | Array[128] | Circular buffer of PosSample |
`mPosFusedHistoryCurrentIdx` | 0-127 | Write index for next sample |

This buffer size provides approximately 12.8 seconds of history at 10 Hz sampling rate, sufficient to match GNSS timestamps that are typically 200-500ms old.

**Sources:** sensors/fusion/sdvpvehiclepositionfuser.h45-66 sensors/fusion/sdvpvehiclepositionfuser.cpp13-18

| Parameter | Default | Description |
|---|---|---|
`mPosGNSSxyStaticGain` | 0.05 | Minimum position correction per update (meters) |
`mPosGNSSxyDynamicGain` | 0.1 | Position correction factor per meter driven |
`mPosGNSSyawGain` | 1.0 | Yaw correction factor per meter driven |
`BIG_DISTANCE_ERROR_m` | 50.0 | Threshold for immediate jump to GNSS position |

The step size for position correction adapts based on vehicle motion:

```
xyStepSize = mPosGNSSxyStaticGain + (distanceDriven * mPosGNSSxyDynamicGain)
```


This allows larger corrections when the vehicle has moved significantly between GNSS updates, reducing lag in the fused estimate.

**Sources:** sensors/fusion/sdvpvehiclepositionfuser.cpp63-108 sensors/fusion/sdvpvehiclepositionfuser.h58-62

The IMU correction handles fast orientation updates and drift compensation:

The algorithm uses static variables to track IMU drift when the vehicle is stopped:

`yawWhenStopping`

`yawDriftSinceStandstill = yawWhenStopping - currentIMUyaw`

and freeze the yaw at `yawWhenStopping`

`mPosIMUyawOffset`

to maintain absolute referenceThis prevents slow drift accumulation during extended standstill periods, which is particularly important for outdoor temperature variations affecting IMU sensors.

**Sources:** sensors/fusion/sdvpvehiclepositionfuser.cpp129-166

Odometry provides dead reckoning between GNSS updates:

The dead reckoning equation is straightforward:

```
x_new = x_current + cos(yaw) * distance
y_new = y_current + sin(yaw) * distance
```


The `mPosOdomDistanceDrivenSinceGNSSupdate`

accumulator tracks total distance (including sign for forward/backward) since the last GNSS update. This value is used by GNSS correction to scale the step size dynamically.

**Sources:** sensors/fusion/sdvpvehiclepositionfuser.cpp110-127

The `getClosestPosFusedSampleInTime()`

function performs a backward search through the circular buffer:

`mPosFusedHistoryCurrentIdx - 1`

)This exploits the temporal ordering of samples for efficient search without requiring a full scan.

**Sources:** sensors/fusion/sdvpvehiclepositionfuser.cpp20-39

When using the u-blox ZED-F9R receiver with on-chip fusion enabled, the algorithm behavior simplifies significantly:

| Aspect | F9P (External Fusion) | F9R (On-Chip Fusion) |
|---|---|---|
| Fusion Location | SDVPVehiclePositionFuser | Inside u-blox receiver |
| History Buffer | Used (128 samples) | Not used |
| IMU Correction | `correctPositionAndYawIMU()` | Handled by F9R |
| Odometry Input | Used for dead reckoning | Sent to F9R as speed data |
| Calibration | Not applicable | ESF sensor calibration required |
| NAV-PVT Rate | Configurable (default 5 Hz) | Configurable with Nav Prio mode |

The F9R requires sensor calibration before producing fused output:

The calibration process typically takes 1-2 minutes of driving with varied maneuvers (turns, acceleration, braking).

**Sources:** sensors/fusion/sdvpvehiclepositionfuser.cpp63-107 sensors/gnss/ubloxrover.cpp44-80 sensors/gnss/ubloxrover.cpp230-247

The fusion algorithm integrates with the multi-source position architecture in `VehicleState`

:

All autopilot systems query `VehicleState::getPosition(PosType::fused)`

to obtain the best available position estimate.

**Sources:** sensors/fusion/sdvpvehiclepositionfuser.cpp63-166 vehicles/vehiclestate.h

The fusion algorithm operates entirely in the local East-North-Up (ENU) coordinate frame:

The ENU reference point is set on the first GNSS fix and remains constant for the session. All subsequent positions are expressed relative to this origin.

**Sources:** sensors/gnss/gnssreceiver.cpp59-104

The `getMaxSignedStepFromValueTowardsGoal()`

function implements bounded correction:

This function ensures corrections approach the target asymptotically without overshooting, providing smooth convergence behavior.

**Sources:** sensors/fusion/sdvpvehiclepositionfuser.cpp51-61

The fusion algorithm can be tuned through three gain parameters:

**Tuning Guidelines:**

| Parameter | Effect if Increased | Effect if Decreased |
|---|---|---|
`xyStaticGain` | Faster position convergence when stopped | Smoother position at standstill |
`xyDynamicGain` | Faster position convergence when moving | Less aggressive GNSS tracking |
`yawGain` | Faster heading convergence | Smoother heading changes |

For F9R on-chip fusion:

**Sources:** sensors/fusion/sdvpvehiclepositionfuser.h36-40 sensors/gnss/ubloxrover.h28-34

| Configuration | Position Latency | Orientation Latency | Update Rate |
|---|---|---|---|
| F9P + External Fusion | ~100-200ms | ~50ms (IMU rate) | 10+ Hz |
| F9R + On-Chip Fusion | ~50-100ms | ~50ms (IMU rate) | 5-10 Hz |
| Pure GNSS (no fusion) | ~300-500ms | Not available | 1-5 Hz |

The external fusion algorithm achieves low latency by:

`128 samples × (16 bytes posXY + 8 bytes yaw + 4 bytes time) = 3.5 KB`

`~4 KB`

The algorithm is designed for resource-constrained embedded systems with minimal memory footprint.

**Sources:** sensors/fusion/sdvpvehiclepositionfuser.h64-66

When position error exceeds 50 meters, the algorithm performs an immediate jump rather than gradual convergence:

This handles scenarios such as:

The algorithm detects reverse driving through the odometry distance sign:

When driving backward, the GNSS heading represents the direction of motion (opposite to vehicle orientation), so 180° is added for correct yaw error calculation.

**Sources:** sensors/fusion/sdvpvehiclepositionfuser.cpp78-82 sensors/fusion/sdvpvehiclepositionfuser.cpp93-101

Typical integration in an application:

**Sources:** sensors/fusion/sdvpvehiclepositionfuser.cpp32-34 sensors/fusion/sdvpvehiclepositionfuser.h27-40

Refresh this wiki
