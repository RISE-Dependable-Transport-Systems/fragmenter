# Source: https://deepwiki.com/das-rise/WayWise/9.3-telemetry-and-diagnostics-ui

The Telemetry & Diagnostics UI components provide specialized interfaces for monitoring vehicle path history, configuring high-precision GNSS infrastructure, and controlling auxiliary hardware such as camera gimbals. These modules are designed as standalone Qt widgets that integrate with the `VehicleConnection`

and `MapWidget`

ecosystems.

The `CameraGimbalUI`

class provides a comprehensive interface for manual and automated control of a vehicle's gimbal system, along with integrated video streaming capabilities.

The UI supports multiple control methods for gimbal pitch and yaw:

`SetRoiByClickOnMapModule`

, which converts map coordinates (ENU) to geodetic coordinates (LLH) before sending them to the gimbal userinterface/cameragimbalui.cpp46-55The interface abstracts the underlying gimbal hardware through the `Gimbal`

base class sensors/camera/gimbal.h11 In MAVLink-based systems, this is implemented by `MavsdkGimbal`

, which uses the MAVSDK Gimbal plugin to communicate with the hardware sensors/camera/mavsdkgimbal.cpp8-10

**Gimbal Control Flow**
Title: Gimbal Control Data Flow

Sources: userinterface/cameragimbalui.cpp198-217 userinterface/cameragimbalui.cpp46-55 sensors/camera/gimbal.h11-24 sensors/camera/mavsdkgimbal.cpp24-38

The UI includes a `QVideoWidget`

for displaying camera feeds. It features a `VideoWidgetEventFilter`

that enables double-click for full-screen toggling userinterface/cameragimbalui.h83-95 The stream is handled via `QMediaPlayer`

, allowing connection to network-based RTSP or MJPEG streams userinterface/cameragimbalui.cpp229-239

The `UbloxBasestationUI`

provides a dedicated interface for managing a GNSS base station, which is essential for providing RTK (Real-Time Kinematic) corrections to vehicles.

The UI allows the user to configure the base station in three primary modes userinterface/ubloxbasestationui.cpp164-172:

The UI provides real-time feedback on the GNSS constellation and RTK status:

`meanAcc`

) and duration (`dur`

) during the survey-in process userinterface/ubloxbasestationui.cpp84-104**Basestation Configuration Flow**
Title: Ublox Basestation Initialization

Sources: userinterface/ubloxbasestationui.cpp164-182 userinterface/ubloxbasestationui.cpp184-194 userinterface/ubloxbasestationui.h49-50

The `TraceUI`

component is a diagnostic tool used to visualize the historical path of a vehicle on the map. It interacts with the `TraceModule`

to record and display position data points.

`VehicleState`

via `setCurrentTraceVehicle`

userinterface/traceui.cpp21-24`TraceModule`

(retrieved via `getTraceModule`

) is registered with the `MapWidget`

to handle the actual rendering of the breadcrumb trail userinterface/traceui.h30-41| Feature | Code Entity | Description |
|---|---|---|
Start Trace | `on_startTraceButton_clicked` | Initiates recording of position points in `TraceModule` . |
Stop Trace | `on_stopTraceButton_clicked` | Ceases recording of new points. |
Clear Trace | `on_clearTraceButton_clicked` | Flushes the buffered position points for the current vehicle. |
Vehicle Link | `setCurrentTraceVehicle` | Binds the UI and module to a specific `VehicleState` instance. |

Sources: userinterface/traceui.cpp21-46 userinterface/traceui.h21-42

Refresh this wiki

This wiki was recently refreshed. Please wait 6 days to refresh again.