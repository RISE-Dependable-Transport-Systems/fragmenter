# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/6.5-camera-control-ui

The Camera Control UI (`CameraGimbalUI`

) provides operator interfaces for controlling camera gimbals and video feeds on vehicles. This page documents the Qt-based user interface components, manual and gamepad-based gimbal control, region-of-interest (ROI) targeting through map integration, video stream display, and camera-specific actuator controls.

For backend gimbal control abstractions and MAVLink protocol usage, see Camera & Gimbal Control. For map visualization and the `MapModule`

extension system, see Map Visualization System.

**Sources:** userinterface/cameragimbalui.h1-117 userinterface/cameragimbalui.cpp1-331

The `CameraGimbalUI`

class is organized into three major functional areas: gimbal control, camera-specific features, and video stream management. It integrates with the map system through a pluggable `MapModule`

and communicates with vehicle hardware through the `Gimbal`

abstraction and `VehicleConnection`

.

**Sources:** userinterface/cameragimbalui.h25-115 userinterface/cameragimbalui.cpp8-22

The interface is divided into three collapsible group boxes, initially disabled until a gimbal is detected. All controls become active upon receiving a valid `Gimbal`

instance through `setGimbal()`

.

| Group Box | Enabled State | Components | Purpose |
|---|---|---|---|
`gimbalControlGroup` | Enabled when gimbal found | 18 directional buttons, zero button, yaw mode buttons, ROI height spinbox | Manual gimbal positioning and mode control |
`cameraControlGroup` | Enabled when gimbal found | 6 actuator buttons (2 groups of 3) | FLIR Pro Duo R camera settings (zoom, video mode) |
`streamGroup` | Always enabled | URL text field, connect/disconnect buttons, video widget | Video stream display and control |

The gimbal control buttons are arranged in a 7×7 grid with three levels of movement precision:

| Button Type | Pitch/Yaw Step | Purpose |
|---|---|---|
| Single arrow | ±1.0° (`SMALL_STEP` ) | Fine adjustments |
| Double arrow | ±5.0° (`MEDIUM_STEP` ) | Medium adjustments |
| Triple arrow | ±20.0° (`BIG_STEP` ) | Coarse positioning |
| Zero button | Reset to 0°, 0° | Return to neutral |

**Sources:** userinterface/cameragimbalui.ui30-295 userinterface/cameragimbalui.h103-108

The `CameraGimbalUI`

maintains internal state for the gimbal's pitch and yaw angles in `mPitchYawState`

(a `QPair<double, double>`

). All directional button clicks call `moveGimbal()`

with delta values, which updates the internal state and enforces angle limits before commanding the gimbal.

The angle limits are hardware-specific constants for the Gremsy Pixy U gimbal:

**Sources:** userinterface/cameragimbalui.cpp198-217 userinterface/cameragimbalui.cpp132-196

The gimbal supports two yaw behavior modes controlled by dedicated buttons:

| Mode | Button | Behavior | Use Case |
|---|---|---|---|
| Yaw Follow | `yawFollowButton` | Yaw follows vehicle heading | Maintain forward-facing camera during maneuvers |
| Yaw Lock | `yawLockButton` | Yaw locked to absolute angle | Point at fixed geographic target while vehicle moves |

These modes are set through `Gimbal::setYawLocked(bool)`

, which maps to `mavsdk::Gimbal::GimbalMode`

in the MAVSDK implementation.

**Sources:** userinterface/cameragimbalui.cpp219-227 sensors/camera/mavsdkgimbal.cpp40-46

The `SetRoiByClickOnMapModule`

is a `MapModule`

implementation that adds right-click functionality to the map for setting gimbal ROI targets. This allows operators to point the camera at specific geographic locations by clicking on the map.

When an ROI is set, `SetRoiByClickOnMapModule::processPaint()`

renders a red circle marker at the target location with a "ROI" text label. The marker persists until a new ROI is set.

**Sources:** userinterface/cameragimbalui.cpp46-100 userinterface/cameragimbalui.h68-81

The Z-coordinate (height above ENU reference) for ROI targets is configured through the `roiHeightSpinBox`

widget, allowing heights up to 999.99 meters. This height is applied when the user clicks on the map, as the map provides only X and Y coordinates.

**Sources:** userinterface/cameragimbalui.ui277-290 userinterface/cameragimbalui.cpp96

The video stream system uses Qt's multimedia framework to display live camera feeds. The implementation supports RTSP and other URL-based video sources.

| Feature | Implementation | Trigger |
|---|---|---|
| Lazy initialization | `QMediaPlayer` created on first connect | Avoids unnecessary resource allocation userinterface/cameragimbalui.cpp231-234 |
| Aspect ratio preservation | `Qt::KeepAspectRatio` mode | Prevents video distortion userinterface/cameragimbalui.cpp14 |
| Fullscreen toggle | `VideoWidgetEventFilter` intercepts double-click | Maximizes video display userinterface/cameragimbalui.h83-95 |
| Auto-show on connect | Widget visibility toggled | Shows only when streaming userinterface/cameragimbalui.cpp236 |
| Auto-hide on disconnect | Widget hidden and fullscreen disabled | Clean state on stop userinterface/cameragimbalui.cpp245-246 |

**Sources:** userinterface/cameragimbalui.cpp229-247 userinterface/cameragimbalui.h83-95

The `cameraControlGroup`

provides hardware-specific controls for the FLIR Pro Duo R camera through actuator outputs. The camera switches modes and zoom levels based on PWM signals sent to auxiliary outputs.

The controls use `VehicleConnection::setActuatorOutput()`

to send normalized PWM values (-1.0, 0.0, +1.0) to specific actuator channels:

**Note:** This implementation is camera-specific. The comment at userinterface/cameragimbalui.h17-18 acknowledges that this should be generalized for other camera systems.

**Sources:** userinterface/cameragimbalui.cpp102-130 userinterface/cameragimbalui.ui298-386

The UI optionally supports gamepad control for gimbal operation, detected automatically when a gimbal becomes available. If a gamepad is connected, the user is prompted with a dialog to enable gamepad control.

When enabled, the gamepad provides continuous gimbal control and camera function access:

| Gamepad Input | Action | Update Rate |
|---|---|---|
| Left stick Y | Pitch adjustment | 150ms timer (`mGamepadTimer` ) |
| Right stick X | Yaw adjustment | 150ms timer |
| L1 button | Actuator 1 → Mid (2x zoom) | On press |
| L2 button | Actuator 1 → High (4x zoom) | On press |
| L3 button | Actuator 1 → Low (1x zoom) | On press |
| R1 button | Actuator 2 → Mid (Thermal) | On press |
| R2 button | Actuator 2 → High (PiP) | On press |
| R3 button | Actuator 2 → Low (RGB) | On press |

The analog stick axes are scaled to produce smooth gimbal movement:

`-4 * axisLeftY()`

(inverted for intuitive up/down) userinterface/cameragimbalui.cpp276`+4 * axisRightX()`

userinterface/cameragimbalui.cpp277A deadzone of 0.05 prevents drift when sticks are centered userinterface/cameragimbalui.cpp279

**Sources:** userinterface/cameragimbalui.cpp256-329 userinterface/cameragimbalui.h113-114

The UI operates on the abstract `Gimbal`

interface, enabling different implementations (MAVSDK-based, custom protocols) without UI changes:

The UI is initialized with references to backend services before becoming operational:

`setGimbal()`

stores the gimbal instance and emits `gotGimbal()`

signal userinterface/cameragimbalui.cpp29-34`setVehicleConnection()`

stores the connection for actuator control userinterface/cameragimbalui.cpp41-44`onGimbalReceived()`

slot (queued connection) enables UI controls and checks for gamepad userinterface/cameragimbalui.cpp249-330This deferred activation pattern ensures thread-safe UI updates when gimbal detection occurs on background threads.

**Sources:** userinterface/cameragimbalui.cpp21 userinterface/cameragimbalui.cpp29-44 sensors/camera/gimbal.h11-24

The `CameraGimbalUI`

provides comprehensive camera and gimbal control through:

`SetRoiByClickOnMapModule`

`Gimbal`

interface, enabling different backend implementationsAll controls remain disabled until a valid gimbal is detected, providing clear status feedback to operators.

**Sources:** userinterface/cameragimbalui.cpp1-331 userinterface/cameragimbalui.h1-117 userinterface/cameragimbalui.ui1-489

Refresh this wiki
