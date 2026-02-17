# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/6.3-ground-vehicle-control-ui

The Ground Vehicle Control UI (`DriveUI`

) provides a Qt-based interface for real-time control and monitoring of ground vehicles. It supports both manual keyboard-based driving and autopilot management, along with vehicle parameter configuration and system administration functions.

This page documents the user interface components specifically for ground vehicles. For drone flight control, see Drone Flight Control UI. For route planning capabilities, see Route Planning Interface.

The `DriveUI`

class serves as the primary ground station interface for interacting with ground vehicles (cars, trucks, and articulated vehicles). It provides:

All vehicle communication is abstracted through the `VehicleConnection`

interface (see Vehicle Connection), enabling consistent control regardless of the underlying communication protocol (MAVLink, ISO22133).

**Sources**: userinterface/driveui.h userinterface/driveui.cpp

**Sources**: userinterface/driveui.h20-67 userinterface/driveui.cpp10-49

The `DriveUI`

interface is organized into functional groups:

| Group | Components | Purpose |
|---|---|---|
Onboard Computer | Vehicle Parameters button Shutdown button Reboot button | System administration and parameter access |
Advanced | Poll ENU ref. button | Coordinate system synchronization |
Manual Control | Throttle progress bar Steering progress bar Autopilot controls | Real-time vehicle control and autopilot state machine |

The autopilot section provides:

**Sources**: userinterface/driveui.ui30-247

The `DriveUI`

widget grabs keyboard focus on initialization and processes arrow key events to generate continuous control signals.

**Sources**: userinterface/driveui.cpp114-152 userinterface/driveui.cpp20-43

The keyboard input is converted to smooth control values using a rate-limited approach:

| Key State | Target Value | Step Size | Result |
|---|---|---|---|
| Up pressed | `1.0` (throttle) | `0.03` | Gradual acceleration forward |
| Down pressed | `-1.0` (throttle) | `0.03` | Gradual acceleration backward |
| Left pressed | `-1.0` (steering) | `0.08` | Gradual left turn |
| Right pressed | `1.0` (steering) | `0.08` | Gradual right turn |
| No key pressed | `0.0` | `0.03/0.08` | Gradual return to neutral |

The `getMaxSignedStepFromValueTowardsGoal()`

function implements a rate limiter that prevents instantaneous changes:

This ensures smooth control transitions at the 25Hz timer rate.

**Sources**: userinterface/driveui.cpp154-164 userinterface/driveui.cpp20-42

Manual control commands are only sent when the vehicle is in `Manual`

flight mode. The mode is checked on each timer iteration:

This safety mechanism prevents keyboard input from interfering with autopilot operation.

**Sources**: userinterface/driveui.cpp40-42

The `DriveUI`

supports two autopilot operational modes:

**Mode 1: Execute Route** - Vehicle follows a pre-uploaded waypoint route using the Pure Pursuit algorithm (see Pure Pursuit Waypoint Follower)

**Mode 2: Follow Point** - Vehicle dynamically tracks a moving target point (see Follow Point Controller)

**Sources**: userinterface/driveui.cpp78-112 userinterface/driveui.ui169-183

The behavior of control buttons varies by mode:

| Button | Execute Route Mode | Follow Point Mode |
|---|---|---|
Start | `startAutopilot()` | `requestFollowPoint()` |
Restart | `restartAutopilot()` - reset route progress | `requestFollowPoint()` - reinitialize tracking |
Pause | `pauseAutopilot()` - pause navigation | Not used |
Stop | `stopAutopilot()` - stop and clear route | `pauseAutopilot()` - stop tracking |

**Sources**: userinterface/driveui.cpp78-112

Routes are received from other UI components (typically Route Planning Interface) via the `gotRouteForAutopilot()`

slot:

The validation ensures that a route contains either all forward motion (speed ≥ 0) or all backward motion (speed < 0), but not a mix. This prevents unsafe direction changes mid-route.

**Sources**: userinterface/driveui.cpp56-76

Vehicles can host multiple autopilot instances with different configurations. The "Set Active Autopilot ID" button allows switching between them:

This feature supports the `MultiWaypointFollower`

system (see Multi-Waypoint Follower), which can manage multiple autopilot strategies simultaneously.

**Sources**: userinterface/driveui.cpp166-177

Clicking the "Vehicle Parameters" button opens a `VehicleParameterUI`

dialog for runtime configuration:

The keyboard is released when the parameter dialog opens to prevent key events from interfering with parameter editing.

**Sources**: userinterface/driveui.cpp179-186

The `VehicleParameterUI`

dialog provides a table-based interface for viewing and modifying parameters:

**Sources**: userinterface/vehicleparameterui.cpp27-173

The system supports three parameter types, each displayed in the table:

| Type | Vehicle Storage | Ground Station Storage | Example Use Cases |
|---|---|---|---|
Int | `int32_t` | `int32_t` | Autopilot ID, iteration counts, enable flags |
Float | `float` | `float` | Pure pursuit gains, speed limits, lookahead distances |
Custom | `std::string` | Not supported | JSON configurations, named modes |

The table displays both vehicle parameters (retrieved via MAVLink) and ground station parameters (from `ParameterServer`

), allowing unified configuration.

**Sources**: userinterface/vehicleparameterui.cpp35-95 userinterface/vehicleparameterui.cpp108-173

**Sources**: userinterface/vehicleparameterui.cpp97-173

The `DriveUI`

provides direct control over the vehicle's onboard computer:

| Button | Action | MAVLink Command | Component Target |
|---|---|---|---|
Reboot | Restart onboard computer | `MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN` `param1 = 0` (reboot) | `OnboardComputer` |
Shutdown | Power down onboard computer | `MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN` `param1 = 2` (shutdown) | `OnboardComputer` |

These commands are useful for remote system maintenance and software update deployment.

**Sources**: userinterface/driveui.cpp188-198

The "Poll ENU ref. from Vehicle" button requests the vehicle's current ENU (East-North-Up) coordinate frame reference point:

This ensures coordinate frame synchronization between the ground station and vehicle, which is critical for accurate position display and route planning. See Coordinate Systems & Transformations for details on ENU reference management.

**Sources**: userinterface/driveui.cpp201-205

**Sources**: All files in this document

The `DriveUI`

maintains minimal internal state, relying primarily on the `VehicleConnection`

abstraction for vehicle state queries:

`mCurrentVehicleConnection`

(set via `setCurrentVehicleConnection()`

)`mArrowKeyStates`

struct (boolean flags)`mKeyControlState`

struct (throttle, steering values)`mVehicleParameterUI`

(lazy-initialized shared pointer)**Sources**: userinterface/driveui.h50-57

Control updates occur at 25Hz (every 40ms) via `mKeyControlTimer`

. This rate balances responsiveness with system load, matching typical RC control update frequencies.

**Sources**: userinterface/driveui.cpp43

Throttle and steering values are displayed using `QProgressBar`

widgets with range `[-100, 100]`

:

This provides real-time visual feedback of the control inputs being sent to the vehicle.

**Sources**: userinterface/driveui.cpp37-38 userinterface/driveui.ui122-156

Refresh this wiki
