# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/6-user-interfaces

WayWise provides Qt5-based user interfaces organized by functional concern: vehicle control (`DriveUI`

, `FlyUI`

), route planning (`PlanUI`

), map visualization (`MapWidget`

), camera control (`CameraGimbalUI`

), and parameter configuration (`VehicleParameterUI`

). All control UIs communicate with backend services through `VehicleConnection`

for vehicle commands and `ParameterServer`

for configuration management, maintaining separation from protocol-specific details.

**Child Pages:**

`MapWidget`

and the `MapModule`

extension system`PlanUI`

and `RoutePlannerModule`

for interactive route creation`DriveUI`

with keyboard control and autopilot management`FlyUI`

for multicopter operations`CameraGimbalUI`

for gimbal and camera control`VehicleParameterUI`

for runtime parameter management**Related Documentation:**

The UI layer separates functional responsibilities across specialized widgets that communicate with backend services through well-defined interfaces:

| UI Component | File | Functional Concern | Backend Interface |
|---|---|---|---|
`DriveUI` | userinterface/driveui.h | Ground vehicle manual/autopilot control | `VehicleConnection` |
`FlyUI` | userinterface/flyui.h | Multicopter flight operations | `VehicleConnection` |
`PlanUI` | userinterface/planui.h | Route creation and management | `RoutePlannerModule` , XML I/O |
`MapWidget` | userinterface/map/mapwidget.h | Map rendering and visualization | `OsmClient` , `ObjectState` list |
`CameraGimbalUI` | userinterface/cameragimbalui.h | Camera/gimbal control | `Gimbal` interface, `VehicleConnection` |
`VehicleParameterUI` | userinterface/vehicleparameterui.h | Parameter viewing/editing | `VehicleConnection` , `ParameterServer` |

This architecture allows UIs to operate without knowledge of MAVLink, MAVSDK, or other protocol-specific implementations.

**Sources:** userinterface/driveui.h20-65 userinterface/flyui.h23-91 userinterface/planui.h26-82 userinterface/cameragimbalui.h25-115

**Title:** UI Layer Communication Pattern with Backend Services

**Sources:** userinterface/driveui.h51-54 userinterface/flyui.h85-89 userinterface/vehicleparameterui.h36-39 userinterface/map/mapwidget.h122-145

All vehicle control UIs follow a standard pattern for backend interaction:

`QSharedPointer<VehicleConnection>`

member (e.g., `mCurrentVehicleConnection`

)`VehicleConnection`

methods`VehicleConnection::getVehicleState()`

Example from `FlyUI`

:

This pattern ensures UIs remain protocol-agnostic and testable with mock backend implementations.

**Sources:** userinterface/flyui.cpp39-44 userinterface/driveui.cpp78-86 userinterface/cameragimbalui.cpp102-105

Control UIs receive their `VehicleConnection`

reference through a setter method, typically called when the application switches active vehicles.

**Title:** VehicleConnection Setup Flow

**Sources:** userinterface/flyui.cpp22-32 userinterface/driveui.cpp51-54

The `FlyUI`

initialization demonstrates creating autopilot components when setting the vehicle connection:

`mCurrentVehicleConnection`

member`FollowPoint`

instance if not already present for follow-point mode**Sources:** userinterface/flyui.cpp22-32

UI button handlers delegate to `VehicleConnection`

methods after null checks:

| Button | Handler | VehicleConnection Method |
|---|---|---|
| Takeoff | `on_takeoffButton_clicked()` | `requestTakeoff()` |
| Land | `on_landButton_clicked()` | `requestLanding()` |
| Arm | `on_armButton_clicked()` | `requestArm()` |
| Disarm | `on_disarmButton_clicked()` | `requestDisarm()` |
| Goto | `on_gotoButton_clicked()` | `requestGotoENU({x, y, z})` |

**Sources:** userinterface/flyui.cpp39-79

Both `DriveUI`

and `FlyUI`

provide two autopilot modes through radio buttons in their UI definitions:

`apExecuteRouteRadioButton`

- follows waypoint sequence`apFollowPointRadioButton`

- tracks dynamic target**Title:** Dual-Mode Autopilot Control Flow

**Sources:** userinterface/flyui.cpp90-130 userinterface/driveui.cpp78-112 userinterface/flyui.ui245-346

The start button handler checks the radio button state to determine which mode to activate:

Similar conditional logic applies to pause/stop/restart buttons.

**Sources:** userinterface/flyui.cpp101-110 userinterface/driveui.cpp88-96

`DriveUI`

implements smooth keyboard control using timer-based interpolation rather than direct key-to-command mapping.

**Title:** Keyboard Control State Machine

The interpolation function `getMaxSignedStepFromValueTowardsGoal()`

ensures smooth transitions by limiting the change per timer tick. This prevents jerky control while maintaining responsiveness.

**Sources:** userinterface/driveui.cpp14-43 userinterface/driveui.cpp154-164 userinterface/driveui.h55-59

`MapWidget`

provides the central map rendering and visualization, with extensibility through the `MapModule`

plugin interface.

| Feature | Implementation | Purpose |
|---|---|---|
| OpenStreetMap tiles | `mOsm` (`OsmClient` ) | Background map imagery |
| Coordinate transforms | `getMousePosRelative()` , `drawTrans` | LLH ↔ ENU ↔ widget coordinates |
| Vehicle display | `mObjectStateMap` (`QMap<int, ObjectState>` ) | Multi-vehicle visualization |
| Grid overlay | `drawGrid()` | Metric reference with labels |
| Module system | `mMapModules` (`QVector<MapModule>` ) | Extensible features |

**Sources:** userinterface/map/mapwidget.h122-145 userinterface/map/mapwidget.cpp729-837

**Title:** MapModule Extension Architecture

**Sources:** userinterface/map/mapwidget.h32-50 userinterface/map/routeplannermodule.h13-67 userinterface/map/tracemodule.h14-45 userinterface/flyui.h72-83

Mouse and keyboard events follow a chain-of-responsibility pattern through registered modules:

**Title:** Map Event Processing Sequence

This allows modules to intercept events for custom behavior (e.g., adding waypoints with Shift+Click) while preserving default map navigation.

**Sources:** userinterface/map/mapwidget.cpp196-238 userinterface/map/mapwidget.cpp308-340

The `TraceModule`

demonstrates the module pattern by tracking and displaying vehicle position history:

`PosType`

has an assignable color**Sources:** userinterface/map/tracemodule.h14-45 userinterface/map/tracemodule.cpp7-36

`VehicleParameterUI`

provides a `QTableWidget`

-based interface for viewing and editing parameters from both vehicle and control station.

**Title:** Parameter UI Workflow

**Sources:** userinterface/vehicleparameterui.cpp27-95 userinterface/vehicleparameterui.cpp97-173

The UI fetches and updates parameters from two independent sources:

| Source | Parameter Types | Fetch Method | Update Method |
|---|---|---|---|
| Vehicle | `int` , `float` , `custom` (string) | `VehicleConnection::getAllParametersFromVehicle()` | `setIntParameterOnVehicle()` `setFloatParameterOnVehicle()` `setCustomParameterOnVehicle()` |
| Control Station | `int` , `float` | `ParameterServer::getInstance()->getAllParameters()` | `ParameterServer::getInstance()->updateIntParameter()` `updateFloatParameter()` |

All parameters are displayed in a single table with columns: **Name** and **Value**.

**Sources:** userinterface/vehicleparameterui.cpp36-95 userinterface/vehicleparameterui.cpp108-173

The `updateChangedParameters()`

method compares table cell values against cached parameter structures, sending updates only for changed values:

This minimizes network traffic by avoiding redundant parameter writes. The method returns `true`

only if at least one parameter was changed and all updates succeeded.

**Sources:** userinterface/vehicleparameterui.cpp108-173

`PlanUI`

provides route creation and management, working in conjunction with `RoutePlannerModule`

for map-based editing.

| Operation | UI Button | Handler Method | Effect |
|---|---|---|---|
| Add Route | `addRouteButton` | `on_addRouteButton_clicked()` | Creates new empty route via `mRoutePlanner->addNewRoute()` |
| Remove Route | `removeRouteButton` | `on_removeRouteButton_clicked()` | Deletes current route via `mRoutePlanner->removeCurrentRoute()` |
| Switch Route | `currentRouteSpinBox` | `on_currentRouteSpinBox_valueChanged()` | Changes active route index |
| Import | `importRouteButton` | `on_importRouteButton_clicked()` | Reads route from XML file |
| Export Current | `exportCurrentRouteButton` | `on_exportCurrentRouteButton_clicked()` | Writes current route to XML with ENU reference |
| Export All | `exportAllRoutesButton` | `on_exportAllRoutesButton_clicked()` | Writes all routes to XML |
| Reverse | `reverseButton` | `on_reverseButton_clicked()` | Reverses waypoint order via `reverseCurrentRoute()` |
| Append | `appendButton` | `on_appendButton_clicked()` | Merges current route into selected route |
| Split | `splitButton` | `on_splitButton_clicked()` | Splits route at selected waypoint connection |
| Send to Autopilot | `sendToAutopilotButton` | `on_sendToAutopilotButton_clicked()` | Emits `routeDoneForUse()` signal |

**Sources:** userinterface/planui.cpp49-74 userinterface/planui.cpp121-259

Point parameters set via `PlanUI`

spin boxes are applied when creating/updating waypoints in `RoutePlannerModule`

:

| Parameter | UI Control | Handler | Conversion | Stored In |
|---|---|---|---|---|
| Height | `heightSpinBox` (m) | `on_heightSpinBox_valueChanged()` | Direct | `setNewPointHeight()` → `PosPoint.height` |
| Speed | `speedSpinBox` (km/h) | `on_speedSpinBox_valueChanged()` | ÷ 3.6 → m/s | `setNewPointSpeed()` → `PosPoint.speed` |
| Attributes | `attributeLineEdit` (hex) | `on_attributeLineEdit_textChanged()` | Parse hex string | `setNewPointAttribute()` → `PosPoint.attributes` |

The `updatePointCheckBox`

determines whether Shift+clicking existing points updates their parameters or leaves them unchanged.

**Sources:** userinterface/planui.cpp76-95 userinterface/planui.ui170-243

`FlyUI`

creates a `GotoWaypointFollower`

instance when setting up the vehicle connection, if a waypoint follower is not already present. This follower is suited for multicopters that accept high-level goto commands.

**Configuration:**

`startFollowingRoute()`

`mCurrentState.repeatRoute`

flagThe implementation issues goto commands via `VehicleConnection::requestGotoENU()`

and monitors distance to current goal.

**Sources:** userinterface/flyui.cpp137-158 autopilot/gotowaypointfollower.cpp45-57 autopilot/gotowaypointfollower.h16-26

Before accepting routes, control UIs perform vehicle-specific safety checks:

**FlyUI Line-of-Sight Validation:**

Default `mLineOfSightDistance`

= 200m, ensuring visual observation capability.

**DriveUI Speed Sign Consistency:**

This prevents unintended direction changes within a single route execution.

**Sources:** userinterface/flyui.cpp137-158 userinterface/driveui.cpp56-76

UI components extend map functionality by providing `MapModule`

subclasses that add right-click context menu options.

`FlyUI`

contains a nested `GotoClickOnMapModule`

class that enables map-click goto commands:

**Class Structure:**

**Context Menu Population:**
When user right-clicks the map, `populateContextMenu()`

returns a menu with "Goto x=..., y=..., z=..." if a vehicle connection exists. The z-coordinate uses the vehicle's current altitude to maintain flight level.

**Action Trigger:**
When the user selects the goto action, the lambda connected to `mGotoAction`

calls:

If autopilot is active, it's automatically stopped before issuing the goto command.

**Sources:** userinterface/flyui.cpp162-212 userinterface/flyui.h72-83

Similarly, `CameraGimbalUI`

provides `SetRoiByClickOnMapModule`

for setting camera region-of-interest by clicking the map:

`roiHeightSpinBox`

in the camera UI`mGimbal->setRegionOfInterest()`

with clicked position**Sources:** userinterface/cameragimbalui.cpp46-100 userinterface/cameragimbalui.h68-81

Control UIs provide access to vehicle system management operations beyond flight/drive commands.

| Command | Available In | Button Handler | VehicleConnection Method | Parameters |
|---|---|---|---|---|
| Reboot | `DriveUI` | `on_requestRebootButton_clicked()` | `requestRebootOrShutdownOfSystemComponents()` | `SystemComponent::OnboardComputer` , `ComponentAction::Reboot` |
| Shutdown | `DriveUI` | `on_requestShutdownButton_clicked()` | `requestRebootOrShutdownOfSystemComponents()` | `SystemComponent::OnboardComputer` , `ComponentAction::Shutdown` |
| Poll ENU Reference | Both | `on_pollENUrefButton_clicked()` | `pollCurrentENUreference()` | None |

The reboot/shutdown commands target the onboard computer, allowing remote system management. The poll ENU reference command queries the vehicle's coordinate frame origin for synchronization.

**Sources:** userinterface/driveui.cpp188-205 userinterface/flyui.cpp223-227 userinterface/driveui.ui30-91

`FlyUI`

implements a multi-vehicle follow feature allowing one multicopter to follow another vehicle's position:

`positionUpdated`

signal`updatePointToFollowInEnuFrame()`

**Implementation:**

The `updateVehicleIdToFollow()`

method establishes the connection:

**Sources:** userinterface/flyui.cpp229-263 userinterface/flyui.ui320-343

Refresh this wiki
