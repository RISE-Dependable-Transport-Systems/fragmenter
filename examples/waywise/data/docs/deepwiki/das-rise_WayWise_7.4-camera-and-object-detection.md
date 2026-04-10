# Source: https://deepwiki.com/das-rise/WayWise/7.4-camera-and-object-detection

The Camera & Object Detection subsystem provides the interface for visual sensors and gimbal control within the WayWise ecosystem. It encompasses high-level abstractions for gimbal hardware, specific implementations for MAVLink-based systems, integration with depth-sensing cameras (OAK-D), and the associated User Interface components for remote operation.

The `DepthAiCamera`

class is designed to handle object detection streams from DepthAI OAK cameras. It operates by parsing a JSON stream delivered over TCP, which typically contains spatial information about detected objects sensors/camera/depthaicamera.h5-15

The camera integration relies on `JsonStreamParserTcp`

to receive newline-delimited JSON objects or arrays communication/jsonstreamparsertcp.h1-15 When a valid JSON array is received, it is processed via `cameraInput()`

to identify and signal the closest detected object sensors/camera/depthaicamera.h21-28

**Object Detection Data Flow**

**Sources:**

WayWise defines a generic `Gimbal`

interface to allow consistent control of camera orientation regardless of the underlying protocol or hardware.

The `Gimbal`

base class defines three primary control methods:

The `MavsdkGimbal`

class implements the interface using the MAVSDK library to communicate with MAVLink-compatible gimbals (e.g., Gremsy Pixy U) sensors/camera/mavsdkgimbal.h14-27 Upon construction, it attempts to take primary control of the gimbal system sensors/camera/mavsdkgimbal.cpp8-21

| Function | MAVSDK Plugin Call |
|---|---|
`setRegionOfInterest` | `set_roi_location_async` sensors/camera/mavsdkgimbal.cpp24-30 |
`setPitchAndYaw` | `set_pitch_and_yaw_async` sensors/camera/mavsdkgimbal.cpp32-38 |
`setYawLocked` | `set_mode_async` (YawLock vs YawFollow) sensors/camera/mavsdkgimbal.cpp40-46 |

**Sources:**

The `CameraGimbalUI`

class provides a comprehensive widget for human-in-the-loop camera operation. It integrates video streaming, manual gimbal movement, and map-based ROI selection.

`QMediaPlayer`

and `QVideoWidget`

to display RTSP or other network streams defined in the `streamUrlEdit`

field userinterface/cameragimbalui.cpp229-239`SMALL_STEP`

(1°), `MEDIUM_STEP`

(5°), and `BIG_STEP`

(20°) userinterface/cameragimbalui.h103-105`MapModule`

called `SetRoiByClickOnMapModule`

. This allows users to right-click on the `MapWidget`

to set the gimbal's ROI to a specific global coordinate userinterface/cameragimbalui.cpp46-55The `moveGimbal`

function handles the accumulation of pitch and yaw requests while enforcing hardware limits. For example, it constrains pitch between -90° and +45° to match standard Gremsy Pixy U firmware limits userinterface/cameragimbalui.cpp198-217

**Sources:**

Refresh this wiki

This wiki was recently refreshed. Please wait 6 days to refresh again.