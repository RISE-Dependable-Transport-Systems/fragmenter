# Source: https://deepwiki.com/das-rise/WayWise/9.2-vehicle-control-panels

The Vehicle Control Panels provide the primary user interface for interacting with vehicles in the WayWise ecosystem. These panels are implemented as Qt Widgets that bridge user input to the underlying `VehicleConnection`

and `WaypointFollower`

logic. They support manual keyboard control, autonomous mission management, and live parameter tuning.

`DriveUI`

is the primary interface for ground vehicles (cars, trucks, and differential drive robots). It provides a dual-mode control scheme: manual arrow-key driving and autopilot mission management.

Manual control is achieved by overriding `keyPressEvent`

and `keyReleaseEvent`

userinterface/driveui.cpp114-152 A `QTimer`

(`mKeyControlTimer`

) runs every 40ms to calculate smoothed throttle and steering values based on the state of `mArrowKeyStates`

userinterface/driveui.cpp20-43

`getMaxSignedStepFromValueTowardsGoal`

is used to ramp acceleration and steering, preventing abrupt changes userinterface/driveui.cpp154-164`FlightMode::Manual`

, the calculated values are sent via `mCurrentVehicleConnection->setManualControl()`

userinterface/driveui.cpp40-41The panel allows users to toggle between "Execute Route" and "Follow Point" modes userinterface/driveui.ui169-184

`gotRouteForAutopilot`

performs a safety check to ensure all nodes have consistent speed signs (either all positive or all negative) userinterface/driveui.cpp56-76`startAutopilot`

, `pauseAutopilot`

, `stopAutopilot`

, and `restartAutopilot`

through the `VehicleConnection`

interface userinterface/driveui.cpp78-112**Sources:** userinterface/driveui.cpp1-206 userinterface/driveui.h1-67 userinterface/driveui.ui1-230

`FlyUI`

provides high-level commands for aerial vehicles, utilizing the MAVLink/MAVSDK backend. It includes specific actions such as Arm, Takeoff, Land, and Return to Home (RTH).

`requestTakeoff()`

, `requestArm()`

, `requestLanding()`

, and `requestPrecisionLanding()`

on the active `VehicleConnection`

userinterface/flyui.cpp39-196`requestGotoENU`

userinterface/flyui.cpp74-79`FlyUI`

implements a nested class `GotoClickOnMapModule`

(a `MapModule`

subclass) userinterface/flyui.h72-83 This allows users to right-click on the map to trigger a "Goto" command at that specific coordinate userinterface/flyui.cpp162-212`FlyUI`

supports a "Follow Vehicle" mode where a drone can track another vehicle. It maintains a list of available `MavsdkVehicleConnection`

objects in a `QComboBox`

to select the target userinterface/flyui.cpp30-32

**Sources:** userinterface/flyui.cpp1-218 userinterface/flyui.h1-93 userinterface/flyui.ui1-250

The `VehicleParameterUI`

provides a spreadsheet-style interface for reading and writing parameters to both the vehicle's onboard computer and the local `ParameterServer`

.

When `on_getAllParametersFromVehicleButton_clicked`

is triggered, the UI fetches all parameters from the `VehicleConnection`

userinterface/vehicleparameterui.cpp27-33

`int`

, `float`

, and `custom`

parameters from the vehicle and the local `ParameterServer`

singleton userinterface/vehicleparameterui.cpp35-41`populateTableWithParameters`

function iterates through these maps, formatting floats to 6 decimal places and populating a `QTableWidget`

userinterface/vehicleparameterui.cpp48-95`updateChangedParameters`

compares current table values against the cached `mVehicleParameters`

. If a change is detected, it calls `setIntParameterOnVehicle`

, `setFloatParameterOnVehicle`

, or `setCustomParameterOnVehicle`

userinterface/vehicleparameterui.cpp108-146**Sources:** userinterface/vehicleparameterui.cpp1-160 userinterface/vehicleparameterui.h1-42

This diagram shows how UI components relate to specific C++ classes and the communication layer.

**Sources:** userinterface/driveui.cpp41 userinterface/flyui.cpp42 userinterface/vehicleparameterui.cpp30-40 autopilot/gotowaypointfollower.h28

The following diagram illustrates the flow of a "Goto" command from the UI to the vehicle logic.

**Sources:** userinterface/flyui.cpp174-175 userinterface/flyui.cpp199-212 autopilot/gotowaypointfollower.cpp129-132

The `SerialPortDialog`

is a utility widget used across various modules (like `MavsdkStation`

or `UbloxBasestationUI`

) to configure serial communication. It allows users to select a system port (e.g., `/dev/ttyUSB0`

) and standard baud rates.

**Sources:** communication/vehicleconnections/mavsdkstation.cpp36-46 userinterface/serialportdialog.h1-20

Refresh this wiki

This wiki was recently refreshed. Please wait 6 days to refresh again.