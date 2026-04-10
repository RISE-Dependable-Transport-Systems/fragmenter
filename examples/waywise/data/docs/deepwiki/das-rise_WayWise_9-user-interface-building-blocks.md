# Source: https://deepwiki.com/das-rise/WayWise/9-user-interface-building-blocks

The `userinterface/`

directory provides a modular library of Qt-based widgets and panels used to build ground station applications. These components range from high-level control dashboards to a flexible, plugin-based map canvas. The UI layer is designed to be "vehicle-aware," connecting to the `VehicleConnection`

abstraction to provide real-time telemetry, parameter management, and autopilot control.

The WayWise UI is built on a decoupled architecture where visual panels interact with the underlying vehicle logic via the `VehicleConnection`

interface.

Title: UI to Vehicle Connection Mapping

**Sources:** userinterface/driveui.cpp40-41 userinterface/flyui.cpp41-43 userinterface/vehicleparameterui.cpp119-120 userinterface/planui.cpp70-74

The `MapWidget`

is the primary visualization component. It uses a custom Qt paint-based engine to render OpenStreetMap (OSM) tiles, vehicle positions, and routes. It employs a **MapModule** plugin pattern, allowing external UI components to inject drawing logic and mouse interaction handlers into the map canvas without modifying the core widget.

`OsmClient`

userinterface/map/mapwidget.h52-148`processPaint`

for custom rendering and `processMouse`

for interaction userinterface/map/mapwidget.h32-50`FlyUI`

use private `MapModule`

implementations to handle "Right-Click to Go-To" functionality on the map userinterface/flyui.cpp162-178For details, see Map Widget & OSM Integration.

**Sources:** userinterface/map/mapwidget.cpp16-55 userinterface/map/mapwidget.h32-50

WayWise provides specialized panels for different vehicle types and operational modes:

| Component | Purpose | Key Features |
|---|---|---|
`DriveUI` | Ground vehicle control | Keyboard manual control (arrow keys), autopilot start/stop, and parameter access userinterface/driveui.h20-65 |
`FlyUI` | Multicopter control | Arm/Disarm, Takeoff, Land, Return-to-Home, and "Goto" coordinate commands userinterface/flyui.h23-91 |
`PlanUI` | Mission planning | Route creation, point-and-click editing via `RoutePlannerModule` , and XML import/export userinterface/planui.h26-82 |
`VehicleParameterUI` | Parameter Management | Live read/write table for MAVLink or internal parameters userinterface/vehicleparameterui.h22-54 |

The `DriveUI`

implements a timer-based manual control loop. It captures keyboard states and translates them into normalized throttle and steering values sent to the vehicle at 25Hz (40ms interval) userinterface/driveui.cpp20-43

For details, see Vehicle Control Panels.

**Sources:** userinterface/driveui.cpp20-43 userinterface/flyui.cpp39-79 userinterface/planui.cpp14-32

Diagnostic tools are integrated into the UI to monitor system health and GNSS performance:

For details, see Telemetry & Diagnostics UI.

**Sources:** userinterface/map/tracemodule.cpp7-25 sensors/gnss/ublox_basestation.cpp10-30

The following diagram illustrates how a UI command (e.g., a "Goto" request) traverses from the User Interface through the Connection layer to the Autopilot.

Title: Goto Command Data Flow

**Sources:** userinterface/flyui.cpp167-177 userinterface/flyui.cpp74-79 communication/vehicleconnections/mavsdkvehicleconnection.cpp200-220

`MapModule`

system.`DriveUI`

, `FlyUI`

, and parameter management.Refresh this wiki

This wiki was recently refreshed. Please wait 6 days to refresh again.