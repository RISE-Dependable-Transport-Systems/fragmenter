# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/6.4-drone-flight-control-ui

`FlyUI`

is a Qt widget that provides flight control operations for multicopter vehicles. It implements basic flight commands (arm, disarm, takeoff, land, return-to-home, precision landing), manual position control via ENU coordinates, autopilot execution modes (Execute Route using `GotoWaypointFollower`

, Follow Point using `FollowPoint`

), and map-based navigation through `GotoClickOnMapModule`

. The UI supports multi-vehicle following with dynamic target position updates.

Related pages: Ground Vehicle Control UI for ground vehicle operations, Camera Control UI for gimbal control, Goto Waypoint Follower and Follow Point Controller for autopilot details.

**Sources:** userinterface/flyui.h1-93 userinterface/flyui.cpp1-264

**Sources:** userinterface/flyui.h85-89 userinterface/flyui.cpp22-32 userinterface/flyui.cpp14

**Sources:** userinterface/flyui.h23-91 userinterface/flyui.cpp22-32

The FlyUI interface is organized into functional groups as defined in the Qt Designer UI file.

| Section | Components | Purpose |
|---|---|---|
Flight Controller | Vehicle Parameters button | Access to runtime parameter configuration |
Advanced | Poll ENU ref. button | Query current ENU reference from vehicle |
Arming | Arm, Disarm buttons | Enable/disable motors |
Flight Operations | Takeoff, Return to Home, Land Here, Precision Land | Basic flight maneuvers |
Position Control | X/Y/Z spinboxes, Go to button, Get Pos. button | Manual ENU coordinate navigation |
Autopilot | Mode selection, transport controls, vehicle follow selector | Mission execution and dynamic following |

**Sources:** userinterface/flyui.ui36-347

The autopilot `QGroupBox`

contains mode selection radio buttons, transport control buttons (restart, start, pause, stop), and a vehicle following combo box.

| UI Element | Widget Name | Purpose |
|---|---|---|
| Execute Route mode | `apExecuteRouteRadioButton` | Selects route execution via `GotoWaypointFollower` |
| Follow Point mode | `apFollowPointRadioButton` | Selects dynamic following via `FollowPoint` |
| Restart button | `apRestartButton` | Restarts active autopilot from beginning |
| Start button | `apStartButton` | Starts selected autopilot mode |
| Pause button | `apPauseButton` | Pauses active autopilot |
| Stop button | `apStopButton` | Stops active autopilot |
| Follow vehicle selector | `followVehicleIdCombo` | Selects lead vehicle for Follow Point mode |

**Sources:** userinterface/flyui.ui245-346

Button click handlers invoke methods on `mCurrentVehicleConnection`

which translate to MAVLink commands.

**Sources:** userinterface/flyui.cpp39-72

| UI Button | Slot Handler | VehicleConnection Method |
|---|---|---|
| Arm | `on_armButton_clicked()` | `requestArm()` |
| Disarm | `on_disarmButton_clicked()` | `requestDisarm()` |
| Takeoff | `on_takeoffButton_clicked()` | `requestTakeoff()` |
| Land Here | `on_landButton_clicked()` | `requestLanding()` |
| Return to Home | `on_returnToHomeButton_clicked()` | `requestReturnToHome()` |
| Precision Land | `on_precisionLandButton_clicked()` | `requestPrecisionLanding()` |

**Sources:** userinterface/flyui.cpp39-72 userinterface/flyui.cpp191-196

Three `QDoubleSpinBox`

widgets (`gotoXSpinBox`

, `gotoYSpinBox`

, `gotoZSpinBox`

) allow entering ENU coordinates. The `gotoButton`

handler reads these values and calls `requestGotoENU()`

:

The `getPositionButton`

handler populates the spinboxes with the current vehicle position from `VehicleState`

:

**Sources:** userinterface/flyui.cpp74-88 userinterface/flyui.ui172-227

Two radio buttons select between Execute Route (using `GotoWaypointFollower`

) and Follow Point (using `FollowPoint`

).

The same branching logic applies to `on_apPauseButton_clicked()`

, `on_apStopButton_clicked()`

, and `on_apRestartButton_clicked()`

.

**Sources:** userinterface/flyui.cpp101-130 userinterface/flyui.ui256-268

The autopilot control buttons (`apStartButton`

, `apPauseButton`

, `apStopButton`

, `apRestartButton`

) check which radio button is active and invoke the corresponding controller methods:

**Sources:** userinterface/flyui.cpp101-130

The `gotRouteForAutopilot()`

slot receives route data from `PlanUI`

, performs line-of-sight validation, and uploads to `VehicleConnection`

.

The `mLineOfSightDistance`

constant (200 meters) enforces visual line-of-sight range from home position.

**Sources:** userinterface/flyui.cpp137-158 userinterface/flyui.h89

The `followVehicleIdCombo`

(`QComboBox`

) selects a lead vehicle. `updateVehicleIdToFollow()`

establishes a signal/slot connection to the lead vehicle's `positionUpdated()`

signal.

Combo box population in `updateFollowVehicleIdComboBox()`

filters out the current vehicle:

The lambda handler adjusts timestamps to UTC before forwarding positions:

**Sources:** userinterface/flyui.cpp229-263

`GotoClickOnMapModule`

is an inner class that implements the `MapModule`

interface for map-based navigation.

**Sources:** userinterface/flyui.h72-83 userinterface/flyui.cpp162-178

`populateContextMenu()`

creates a context menu entry for clicked map positions:

Behavior details:

`nullptr`

if `mCurrentVehicleConnection`

is null (no menu shown)`yaw=true`

to `requestGotoENU()`

for heading control**Sources:** userinterface/flyui.cpp167-177 userinterface/flyui.cpp199-212

`setCurrentVehicleConnection()`

initializes the UI for a vehicle and creates a `FollowPoint`

controller if needed.

**Sources:** userinterface/flyui.cpp22-32

`on_vehicleParameterButton_clicked()`

opens `VehicleParameterUI`

:

`on_pollENUrefButton_clicked()`

queries the vehicle's ENU reference:

See Parameter Configuration UI for parameter management details. See Coordinate Systems & Transformations for ENU reference usage.

**Sources:** userinterface/flyui.cpp214-227

`GotoWaypointFollower`

is created lazily in `gotRouteForAutopilot()`

when the first route is received:

The follower uses `PosType::defaultPosType`

for position source selection. See Goto Waypoint Follower for algorithm details.

**Sources:** userinterface/flyui.cpp139-143

**Sources:** userinterface/flyui.cpp39-130 autopilot/gotowaypointfollower.cpp109-172

The FlyUI integrates with multiple subsystems:

| Subsystem | Interface | Purpose |
|---|---|---|
| VehicleConnection | `mCurrentVehicleConnection` | Command transmission to vehicle |
| GotoWaypointFollower | Created via `setWaypointFollowerConnectionLocal()` | Route execution autopilot |
| FollowPoint | Created via `setFollowPointConnectionLocal()` | Dynamic target tracking |
| MapWidget | `mGotoClickOnMapModule` | Visual navigation interface |
| VehicleParameterUI | `mVehicleParameterUI` | Runtime parameter configuration |
| VehicleState | Via `VehicleConnection::getVehicleState()` | Position queries |

**Sources:** userinterface/flyui.h85-89 userinterface/flyui.cpp22-32

The `FlyUI`

widget provides comprehensive quadcopter control through a layered architecture:

The UI is defined in userinterface/flyui.ui implemented in userinterface/flyui.cpp and uses `GotoWaypointFollower`

(autopilot/gotowaypointfollower.cpp) for route execution.

**Sources:** userinterface/flyui.h1-93 userinterface/flyui.cpp1-264 userinterface/flyui.ui1-355

Refresh this wiki
