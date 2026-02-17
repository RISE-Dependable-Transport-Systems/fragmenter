# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/5.4-basestation-configuration-(ubloxbasestation)

This document describes the `UbloxBasestation`

class, which configures and manages u-blox GNSS receivers operating as RTK basestations. The basestation generates RTCM correction data that rovers use to achieve centimeter-level positioning accuracy. This covers the three operating modes (Fixed, MovingBase, SurveyIn), configuration procedures, and RTCM message generation.

For information about rover-side GNSS positioning, see GNSS & RTK Positioning. For sensor fusion that consumes the corrected position data, see Sensor Fusion Algorithm.

**Sources:** sensors/gnss/ublox_basestation.h1-60 sensors/gnss/ublox_basestation.cpp1-220

The `UbloxBasestation`

class provides a high-level interface for configuring u-blox ZED-F9P or ZED-F9R receivers as RTK basestations. It wraps the low-level `Ublox`

class and handles all configuration details automatically.

**Sources:** sensors/gnss/ublox_basestation.h18-58 sensors/gnss/ublox_basestation.cpp10-44

The `UbloxBasestation`

supports three operating modes defined by the `BasestationMode`

enumeration. Each mode serves different use cases with different accuracy and mobility characteristics.

| Mode | Use Case | Position Source | Mobility | Accuracy |
|---|---|---|---|---|
Fixed | Permanent installation with known position | User-provided lat/lon/height | Stationary | Highest (position is exact) |
SurveyIn | Temporary installation with unknown position | Self-surveyed over time | Stationary | High (depends on survey duration) |
MovingBase | Mobile basestation for moving baseline RTK | Real-time GNSS position | Mobile | Lower (position from GNSS) |

In Fixed mode, the basestation transmits corrections based on a user-specified position. This mode provides the highest accuracy when the exact position is known from a survey.

**Configuration parameters:**

`fixedRefLat`

- Latitude in degrees`fixedRefLon`

- Longitude in degrees`fixedRefHeight`

- Height in meters (ellipsoid)**RTCM messages:** Full message set including stationary reference position (1005) and high-precision observations (1077, 1087, 1097, 1127).

In SurveyIn mode, the basestation autonomously determines its position by averaging measurements over time. Once the position meets the accuracy and duration criteria, the basestation begins transmitting corrections.

**Configuration parameters:**

`surveyInMinAcc`

- Minimum position accuracy in meters (default: 2.0 m)`surveyInMinDuration`

- Minimum survey duration in seconds (default: 60 s)**Status monitoring:** The `rxSvin`

signal emits `ubx_nav_svin`

messages containing survey progress (observations, mean position, accuracy).

In MovingBase mode, the basestation is mobile and transmits corrections based on its current GNSS position. This enables moving baseline RTK, where both basestation and rover are in motion.

**RTCM messages:** Reduced message set optimized for bandwidth (1074, 1084, 1094, 1124 instead of 1077, 1087, 1097, 1127). Omits stationary reference position (1005).

**Sources:** sensors/gnss/ublox_basestation.h22-23 sensors/gnss/ublox_basestation.cpp94-128 sensors/gnss/ublox_basestation.cpp140-160

The `BasestationConfig`

structure encapsulates all configuration parameters for the basestation. A default configuration is provided as `UbloxBasestation::defaultConfig`

.

| Parameter | Type | Default | Description |
|---|---|---|---|
`mode` | `BasestationMode` | `SurveyIn` | Operating mode (Fixed, MovingBase, SurveyIn) |
`baudrate` | `unsigned` | 921600 | Serial port baud rate |
`measurementRate` | `unsigned` | 1 Hz | GNSS measurement frequency |
`navSolutionRate` | `unsigned` | 1 | Navigation solutions per measurement (1 = every measurement) |
`fixedRefLat` | `double` | -1 | Fixed mode: latitude in degrees |
`fixedRefLon` | `double` | -1 | Fixed mode: longitude in degrees |
`fixedRefHeight` | `double` | -1 | Fixed mode: ellipsoid height in meters |
`surveyInMinAcc` | `double` | 2.0 m | SurveyIn mode: minimum position accuracy |
`surveyInMinDuration` | `unsigned` | 60 s | SurveyIn mode: minimum survey duration |

**Sources:** sensors/gnss/ublox_basestation.h23-33 sensors/gnss/ublox_basestation.cpp8

The configuration process occurs automatically when calling `connectSerial()`

. The following diagram shows the sequence of UBX commands sent to the receiver.

**1. UART Configuration (sensors/gnss/ublox_basestation.cpp74-83)**

`ubxCfgPrtUart()`

**2. Message Rate Configuration (sensors/gnss/ublox_basestation.cpp85)**

`ubxCfgRate()`

**3. UBX Message Enable/Disable (sensors/gnss/ublox_basestation.cpp88-127)**

`ubxCfgMsg()`

for each message type**4. GNSS System Enablement (sensors/gnss/ublox_basestation.cpp130-137)**

`ubloxCfgValset()`

with constellation configuration**5. Time Mode Configuration (sensors/gnss/ublox_basestation.cpp139-160)**

`mode = 0`

(disabled)`mode = 1`

, with `svin_min_dur`

and `svin_acc_limit`

`mode = 2`

, with LLA coordinates and `lla = true`

`ubxCfgTmode3()`

**6. Dynamic Model (sensors/gnss/ublox_basestation.cpp163-168)**

`dyn_model = 2`

) for optimal basestation performance`ubxCfgNav5()`

**7. Time Pulse Configuration (sensors/gnss/ublox_basestation.cpp171-189)**

`ubloxCfgTp5()`

**8. Save Configuration (sensors/gnss/ublox_basestation.cpp192-206)**

`ubloxCfgCfg()`

**Sources:** sensors/gnss/ublox_basestation.cpp67-209

Different RTCM messages are enabled based on the basestation mode. The configuration optimizes for either stationary basestations (Fixed/SurveyIn) or mobile basestations (MovingBase).

| Message | Description | Fixed/SurveyIn | MovingBase |
|---|---|---|---|
1005 | Stationary RTK reference station ARP | ✓ | ✗ |
1074 | GPS MSM4 (medium-precision) | ✓ | ✓ |
1077 | GPS MSM7 (high-precision) | ✓ | ✗ |
1084 | GLONASS MSM4 | ✓ | ✓ |
1087 | GLONASS MSM7 | ✓ | ✗ |
1094 | Galileo MSM4 | ✓ | ✓ |
1097 | Galileo MSM7 | ✓ | ✗ |
1124 | BeiDou MSM4 | ✓ | ✓ |
1127 | BeiDou MSM7 | ✓ | ✗ |
1230 | GLONASS code-phase biases | ✓ | ✓ |
4072.0 | Reference station PVT (u-blox proprietary) | ✓ | ✓ |
4072.1 | Additional reference station info | ✗ | ✗ |

**Fixed/SurveyIn Mode:**

**MovingBase Mode:**

The basestation applies bandwidth optimization by throttling the reference position messages (1005, 1006). These are transmitted only every 5th cycle rather than every cycle.

This reduces data rate while maintaining sufficient position updates for rover initialization.

**Sources:** sensors/gnss/ublox_basestation.cpp94-127 sensors/gnss/ublox_basestation.cpp32-44

The `UbloxBasestation`

emits Qt signals for asynchronous data delivery to the application. These signals connect to the underlying `Ublox`

class signals.

| Signal | Parameters | Description | Emission Frequency |
|---|---|---|---|
`rtcmData` | `QByteArray data, int type` | RTCM correction message with message type | Every measurement (throttled for 1005) |
`currentPosition` | `llh_t llh` | Current basestation position from UBX-NAV-PVT | Every navigation solution (default: 1 Hz) |
`rxNavSat` | `ubx_nav_sat sat` | Satellite visibility and signal information | 1 Hz (if enabled) |
`rxSvin` | `ubx_nav_svin svin` | Survey-in status (observations, accuracy, valid flag) | 1 Hz in SurveyIn mode |
`rxCfgGnss` | `ubx_cfg_gnss gnss` | GNSS configuration response | On demand (pollCfgGNSS) |
`rxMonVer` | `QString sw, QString hw, QStringList ext` | Receiver version information | On demand (pollMonVer) |

**RTCM Data Broadcasting:**

**Position Monitoring:**

**Survey-In Progress:**

**Sources:** sensors/gnss/ublox_basestation.h45-51 sensors/gnss/ublox_basestation.cpp12-44

The `UbloxBasestation`

integrates with the WayWise system through the communication layer. The basestation typically runs on a ground station computer and broadcasts RTCM data to rovers via `MavsdkStation`

.

The basestation position often serves as the ENU (East-North-Up) coordinate system reference for the entire system. In the provided code, `MapWidget`

has a hardcoded reference position:

In a typical deployment:

`MapWidget::setEnuRef()`

The RTCM data generated by the basestation follows this path:

`UbloxBasestation::rtcmData`

signal emits each message with type identifier`MavsdkStation::broadcastRtcmData()`

sends to all connected vehicles`GPS_RTCM_DATA`

MAVLink messages`UbloxRover`

receives via `MavsdkVehicleServer`

and feeds to receiver**Sources:** userinterface/map/mapwidget.cpp42-43 sensors/gnss/ublox_basestation.cpp32-44

Typical initialization sequence for a basestation application:

**Alternative: Fixed Mode Setup**

**Sources:** sensors/gnss/ublox_basestation.h23-42 sensors/gnss/ublox_basestation.cpp47-58

Refresh this wiki
