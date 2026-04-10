# Source: https://deepwiki.com/das-rise/WayWise/1.1-getting-started-and-examples

This page provides a technical guide on integrating WayWise into your projects and explores the provided example applications. WayWise is designed to be used as a library (typically via git submodule) to provide autonomous navigation, vehicle state management, and communication capabilities to various robotic platforms.

WayWise uses CMake as its build system and depends heavily on the Qt5 framework. To integrate WayWise into an external project, it is recommended to add it as a git submodule and include its source files in your `CMakeLists.txt`

.

`Core`

, `Network`

, `SerialPort`

, `Widgets`

, `PrintSupport`

examples/map_local_twocars/CMakeLists.txt21`-Wall -Wextra -Wpedantic`

examples/RCCar_MAVLINK_autopilot/CMakeLists.txt17-19The examples demonstrate a pattern where `WAYWISE_PATH`

is defined to point to the library root, and specific source files are added to the executable target. This allows for lean builds containing only the necessary subsystems.

**Sources:** examples/RCCar_MAVLINK_autopilot/CMakeLists.txt24-55 examples/RCCar_MAVLINK_autopilot/README.md7-17

The `RCCar_MAVLINK_autopilot`

example demonstrates a minimal Ackermann-style vehicle that communicates with a ground station (like ControlTower) using the MAVLink protocol via the MAVSDK library.

The application initializes a `CarState`

to represent the physical vehicle and a `MavsdkVehicleServer`

to handle MAVLink telemetry and commands. A `CarMovementController`

manages the simulated or physical actuators, while a `PurepursuitWaypointFollower`

provides the logic for following uploaded routes.

The following diagram shows how MAVLink commands move through the system to influence vehicle state.

**MAVLink Command to Actuation**

**Key Implementation Points:**

`QTimer`

triggers `simulationStep`

every 25ms examples/RCCar_MAVLINK_autopilot/main.cpp14-27`CarMovementController`

emits `updatedOdomPositionAndYaw`

, which is used to update the `fused`

position in `VehicleState`

examples/RCCar_MAVLINK_autopilot/main.cpp27-32`provideParametersToParameterServer()`

method is called on the state, server, and follower to expose internal variables to the MAVLink parameter protocol examples/RCCar_MAVLINK_autopilot/main.cpp44-46**Sources:** examples/RCCar_MAVLINK_autopilot/main.cpp9-64 examples/RCCar_MAVLINK_autopilot/CMakeLists.txt26-54

This example (`RCCar_ISO22133_autopilot`

) replaces the MAVLink communication layer with an `iso22133VehicleServer`

. This protocol is used for industrial automated guided vehicles (AGVs) and heavy machinery.

The structure is nearly identical to the MAVLink example, highlighting the modularity of the WayWise `VehicleServer`

abstraction.

**ISO 22133 Integration**

**Key Implementation Points:**

`CarMovementController`

and `PurepursuitWaypointFollower`

to bridge protocol messages (like "Start Trajectory") to autopilot actions examples/RCCar_ISO22133_autopilot/main.cpp41-42**Sources:** examples/RCCar_ISO22133_autopilot/main.cpp10-60 examples/RCCar_ISO22133_autopilot/CMakeLists.txt28-55

The `map_local_twocars`

example demonstrates the `userinterface`

module, specifically the `MapWidget`

. It visualizes two independent `CarState`

objects on a 2D map.

Unlike the autopilot examples, this is a `QMainWindow`

application. It uses the `MapWidget`

to render the vehicles in real-time.

`ui->mapWidget->addObjectState(car1)`

examples/map_local_twocars/mainwindow.cpp13`CarMovementController`

are created, each driving a separate `CarState`

with different steering and speed inputs examples/map_local_twocars/mainwindow.cpp17-37`coordinatetransforms.h`

to manage the relationship between local ENU coordinates and the visual map examples/map_local_twocars/CMakeLists.txt40**Sources:** examples/map_local_twocars/mainwindow.cpp4-45 examples/map_local_twocars/mainwindow.h13-29

WayWise includes a `routeplanning`

module used in these examples to generate and manipulate paths.

The `ZigZagRouteGenerator`

class provides static methods to fill convex polygons with efficient traversal patterns.

`RouteUtils`

provides `readRouteFromFile`

, which handles XML-based route definitions and performs ENU reference frame transformations to ensure the route is correctly positioned relative to the vehicle's origin routeplanning/routeutils.cpp7-79| Function | Purpose |
|---|---|
`distanceToLine` | Calculates the perpendicular distance from a `PosPoint` to a line segment routeplanning/zigzagroutegenerator.cpp13 |
`isPointWithin` | Determines if a coordinate is inside a polygon defined by a list of `PosPoint` routeplanning/routeutils.cpp81 |
`getShrinkedConvexPolygon` | Offsets polygon boundaries inward by a specified spacing routeplanning/zigzagroutegenerator.h28 |

**Sources:** routeplanning/zigzagroutegenerator.cpp8-165 routeplanning/routeutils.cpp7-106

Refresh this wiki

This wiki was recently refreshed. Please wait 7 days to refresh again.