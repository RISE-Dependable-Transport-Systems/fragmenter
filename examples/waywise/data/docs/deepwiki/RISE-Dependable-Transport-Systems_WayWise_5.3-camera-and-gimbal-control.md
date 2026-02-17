# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/5.3-camera-and-gimbal-control

The camera and gimbal control subsystem provides abstractions and user interfaces for controlling camera gimbals mounted on vehicles. Key capabilities include pitch/yaw positioning, region-of-interest (ROI) targeting, yaw lock modes, and camera-specific features (zoom, thermal/RGB switching) through actuator control. The implementation uses the MAVLink GIMBAL_MANAGER protocol via MAVSDK plugins.

**Core Components:**

`Gimbal`

- Abstract interface for gimbal control`MavsdkGimbal`

- MAVLink implementation using MAVSDK gimbal plugin`CameraGimbalUI`

- Qt widget for operator control`SetRoiByClickOnMapModule`

- Map-based ROI targeting extensionRelated pages: Map Visualization System, Ground Vehicle Control UI, Drone Flight Control UI, Vehicle Connection

The camera and gimbal control system consists of three main layers:

**Sources:** sensors/camera/gimbal.h1-27 sensors/camera/mavsdkgimbal.h1-30 userinterface/cameragimbalui.h1-118

The `Gimbal`

class defines the abstract interface for all gimbal implementations. It provides three core capabilities:

| Method | Purpose | Parameters |
|---|---|---|
`setRegionOfInterest(llh_t)` | Point gimbal at geographic location | Latitude, longitude, height |
`setRegionOfInterest(xyz_t, llh_t)` | Point gimbal at ENU coordinates | ENU position, reference point |
`setPitchAndYaw(double, double)` | Set absolute gimbal orientation | Pitch (degrees), Yaw (degrees) |
`setYawLocked(bool)` | Control yaw follow/lock mode | Lock state |

The interface uses coordinate transformation utilities to convert between ENU (East-North-Up) coordinates and LLH (Latitude-Longitude-Height) for geographic positioning.

**Sources:** sensors/camera/gimbal.h11-24

The `MavsdkGimbal`

class implements the `Gimbal`

interface using the MAVSDK gimbal plugin. It communicates with MAVLink-compatible gimbal controllers.

During construction, `MavsdkGimbal`

takes primary control of the gimbal:

`mavsdk::Gimbal`

instance from the provided systemsensors/camera/mavsdkgimbal.cpp8-21

Each `Gimbal`

method translates to corresponding MAVSDK async operations that send MAVLink GIMBAL_MANAGER protocol commands:

| Gimbal Method | MAVSDK Call | MAVLink Command Message |
|---|---|---|
`setRegionOfInterest()` | `set_roi_location_async()` | `MAV_CMD_DO_SET_ROI_LOCATION` |
`setPitchAndYaw()` | `set_pitch_and_yaw_async()` | `MAV_CMD_DO_GIMBAL_MANAGER_PITCHYAW` |
`setYawLocked(true)` | `set_mode_async(YawLock)` | `MAV_CMD_DO_GIMBAL_MANAGER_CONFIGURE` |
`setYawLocked(false)` | `set_mode_async(YawFollow)` | `MAV_CMD_DO_GIMBAL_MANAGER_CONFIGURE` |

All operations execute asynchronously with callback handlers that log warnings on failure. The MAVSDK gimbal plugin handles the MAVLink message construction and response handling.

**Sources:** sensors/camera/mavsdkgimbal.cpp24-46

The `CameraGimbalUI`

class (`userinterface/cameragimbalui.h`

, `userinterface/cameragimbalui.cpp`

) provides a Qt-based control interface with four functional groups:

**CameraGimbalUI Component Structure:**

**Sources:** userinterface/cameragimbalui.h25-115 userinterface/cameragimbalui.cpp1-331 userinterface/cameragimbalui.ui1-490

The UI provides incremental pitch and yaw control with three step sizes:

| Step Size | Constant | Degrees | UI Buttons |
|---|---|---|---|
| Small | `SMALL_STEP` | 1.0° | Single arrow buttons |
| Medium | `MEDIUM_STEP` | 5.0° | Double arrow buttons |
| Large | `BIG_STEP` | 20.0° | Triple arrow buttons |

The `moveGimbal()`

method maintains internal state and enforces range limits:

userinterface/cameragimbalui.h102-108 userinterface/cameragimbalui.cpp198-217

The FLIR Pro Duo R dual-camera system (RGB + thermal) is controlled via PWM actuator outputs through the `VehicleConnection::setActuatorOutput()`

method:

**FLIR Pro Duo R Control Flow:**

**FLIR Pro Duo R Actuator Mappings:**

| Actuator Channel | Value | Function | UI Button |
|---|---|---|---|
| 1 | -1.0 | RGB Zoom 1x | `actuatorOneLowButton` |
| 1 | 0.0 | RGB Zoom 2x | `actuatorOneMidButton` |
| 1 | 1.0 | RGB Zoom 4x | `actuatorOneHighButton` |
| 2 | -1.0 | Video Mode: RGB | `actuatorTwoLowButton` |
| 2 | 0.0 | Video Mode: Thermal | `actuatorTwoMidButton` |
| 2 | 1.0 | Video Mode: PiP (Picture-in-Picture) | `actuatorTwoHighButton` |

The implementation is camera-specific and hardcoded for FLIR Pro Duo R. Future camera integrations would require generalization of the actuator control interface.

**Sources:** userinterface/cameragimbalui.cpp102-130 userinterface/cameragimbalui.h17-19

The `SetRoiByClickOnMapModule`

class (inner class of `CameraGimbalUI`

) extends `MapModule`

to enable map-based ROI targeting:

**Map-Based ROI Targeting Sequence:**

The module also renders the current ROI location (`mLastRoiSet`

) on the map as a red circle with "ROI" label via the `processPaint()`

method.

**Sources:** userinterface/cameragimbalui.cpp46-100 userinterface/cameragimbalui.h68-81

The ROI height is configurable via `roiHeightSpinBox`

in the UI, allowing users to set the target altitude for the gimbal focus point (range: 0-999.99 meters).

userinterface/cameragimbalui.ui277-290

The gimbal supports two yaw operational modes:

| Mode | Behavior | Use Case |
|---|---|---|
Yaw Follow | Yaw rotates with vehicle heading | Vehicle-relative targeting |
Yaw Lock | Yaw maintains absolute compass direction | Fixed geographic targeting |

These modes are controlled via dedicated buttons in the UI that call `Gimbal::setYawLocked()`

.

**Sources:** userinterface/cameragimbalui.cpp219-227

When a gamepad is detected at initialization, `CameraGimbalUI::onGimbalReceived()`

displays a `QMessageBox`

asking the user for permission to use it for gimbal control.

**Gamepad Control Initialization:**

**Gamepad Control Behavior:**

`mGamepadTimer`

polls at 150ms intervals`moveGimbal(movePitchDeg, moveYawDeg)`

**Sources:** userinterface/cameragimbalui.cpp256-329 userinterface/cameragimbalui.h113-114

The UI integrates a video player for displaying camera feeds:

The `videoWidget`

(`QVideoWidget`

) is configured in the constructor:

`Qt::AspectRatioMode::KeepAspectRatio`

`VideoWidgetEventFilter`

installed to handle double-click for fullscreen toggle**Sources:** userinterface/cameragimbalui.cpp13-16 userinterface/cameragimbalui.h83-95

The video streaming functionality uses `mMediaPlayer`

(`QMediaPlayer`

):

**Video Stream State Machine:**

**Default Configuration:**

`rtsp://192.168.43.1:8554/fpv_stream`

(configurable via `streamUrlEdit`

)**Sources:** userinterface/cameragimbalui.cpp229-247 userinterface/cameragimbalui.ui389-430 userinterface/cameragimbalui.h110-111

`CameraGimbalUI`

requires a `VehicleConnection`

instance for actuator control:

This enables:

userinterface/cameragimbalui.cpp41-44

The UI uses Qt's signal-slot mechanism with `QueuedConnection`

to ensure gimbal initialization occurs on the Qt UI thread:

When `setGimbal()`

is called (potentially from a background thread), it emits `gotGimbal`

, which queues `onGimbalReceived()`

for execution in the UI thread.

**Sources:** userinterface/cameragimbalui.cpp21-34

The gimbal interface handles coordinate conversions transparently:

This allows the UI to work with map-local coordinates while the MAVSDK interface requires global geographic coordinates.

**Sources:** sensors/camera/gimbal.h16-18

The UI is currently configured for the **Gremsy Pixy U** gimbal with firmware 7.5.6:

These constants are defined in `CameraGimbalUI`

and should be adjusted for different gimbal models.

userinterface/cameragimbalui.h106-108

The "FLIR Pro Duo R control" group box contains hardcoded settings for this specific dual-camera system. Future camera integrations would require generalization of the actuator control interface, as noted in the code comments.

Refresh this wiki
