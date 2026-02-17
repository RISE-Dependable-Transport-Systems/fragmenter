# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/1.2-getting-started

This page guides you through building and running WayWise example applications. It covers system requirements, dependency installation, the CMake build process, and basic configuration for the three provided examples: `RCCar_ISO22133_autopilot`

, `RCCar_MAVLINK_autopilot`

, and `map_local_twocars`

.

For detailed information about the system architecture and how components interact, see Architecture & System Design. For information about specific subsystems, refer to the specialized pages: Communication Layer for MAVLink/ISO22133 protocols, Autopilot Systems for route following, Vehicle State Management for vehicle models, and User Interfaces for GUI applications.

WayWise is developed and tested on Linux systems. The codebase uses POSIX-compliant components and Qt5 for cross-platform compatibility.

| Dependency | Minimum Version | Purpose | Components Using It |
|---|---|---|---|
Qt5 | 5.x | Core framework, networking, GUI, serial communication | All examples |
CMake | 3.5 | Build system | All examples |
MAVSDK | Latest | MAVLink communication library | `RCCar_MAVLINK_autopilot` , `RCCar_ISO22133_autopilot` |
C++17 compiler | - | Language standard | All examples |
C23 compiler | - | For C components | All examples |

Sources: examples/RCCar_ISO22133_autopilot/CMakeLists.txt21 examples/RCCar_MAVLINK_autopilot/CMakeLists.txt21 examples/map_local_twocars/CMakeLists.txt21

WayWise uses CMake with a shared source file structure. All examples reference the core WayWise codebase through the `WAYWISE_PATH`

variable, which points to the repository root.

Sources: examples/RCCar_ISO22133_autopilot/CMakeLists.txt24 examples/RCCar_MAVLINK_autopilot/CMakeLists.txt24 examples/map_local_twocars/CMakeLists.txt23

The build configuration uses several important variables:

| Variable | Value | Purpose |
|---|---|---|
`CMAKE_CXX_STANDARD` | `17` | C++ language standard |
`CMAKE_C_STANDARD` | `23` | C language standard |
`WAYWISE_PATH` | `../..` | Relative path to repository root |
`CMAKE_AUTOUIC` | `ON` | Automatic Qt UI file processing |
`CMAKE_AUTOMOC` | `ON` | Automatic Qt meta-object compilation |
`CMAKE_AUTORCC` | `ON` | Automatic Qt resource compilation |

Sources: examples/RCCar_ISO22133_autopilot/CMakeLists.txt7-15 examples/RCCar_MAVLINK_autopilot/CMakeLists.txt7-15 examples/map_local_twocars/CMakeLists.txt7-15

Sources: examples/RCCar_ISO22133_autopilot/CMakeLists.txt28-55 examples/RCCar_MAVLINK_autopilot/CMakeLists.txt26-54 examples/map_local_twocars/CMakeLists.txt25-51

**Purpose**: Vehicle-side autopilot using ISO 22133 communication protocol.

**Key Components**:

`ISO22133VehicleServer`

- Implements ISO 22133 protocol server`PurepursuitWaypointFollower`

- Pure pursuit path tracking algorithm`UbloxRover`

- u-blox GNSS receiver integration`CarState`

- Ackermann vehicle model`ISO_object`

library - ISO 22133 message encoding/decoding**Use Case**: Deploy on embedded Linux system (e.g., Raspberry Pi) connected to vehicle hardware. Receives commands from ground station using ISO 22133 protocol over UDP or serial.

Sources: examples/RCCar_ISO22133_autopilot/CMakeLists.txt28-63

**Purpose**: Vehicle-side autopilot using MAVLink communication protocol.

**Key Components**:

`MavsdkVehicleServer`

- Implements MAVLink server using MAVSDK`PurepursuitWaypointFollower`

- Pure pursuit path tracking algorithm`UbloxRover`

- u-blox GNSS receiver integration`CarState`

- Ackermann vehicle model`MavlinkParameterServer`

- MAVLink-compatible parameter management**Use Case**: Deploy on embedded Linux system connected to vehicle hardware. Compatible with QGroundControl, Mission Planner, and other MAVLink ground stations.

**Default Port**: UDP 14540 (standard MAVSDK vehicle-side port)

Sources: examples/RCCar_MAVLINK_autopilot/CMakeLists.txt26-62

**Purpose**: Local visualization and simulation of multiple vehicles with map-based interface.

**Key Components**:

`MainWindow`

- Qt GUI main window`MapWidget`

- OpenStreetMap-based visualization`OsmClient`

- OpenStreetMap tile download and caching`PurepursuitWaypointFollower`

- Path tracking for simulated vehicles`CarState`

(2 instances) - Two simulated vehicles**Use Case**: Local testing, route planning visualization, multi-vehicle scenario simulation without physical hardware.

Sources: examples/map_local_twocars/CMakeLists.txt25-59

**Ubuntu/Debian**:

This example requires the `ISO_object`

library, which is included as a subdirectory:

The build process:

`isoObject`

subdirectory first examples/RCCar_ISO22133_autopilot/CMakeLists.txt26`RCCar_ISO22133_autopilot`

Sources: examples/RCCar_ISO22133_autopilot/CMakeLists.txt1-64

Requires MAVSDK to be installed system-wide:

The build process:

`find_package(MAVSDK REQUIRED)`

examples/RCCar_MAVLINK_autopilot/CMakeLists.txt22`RCCar_MAVLINK_autopilot`

Sources: examples/RCCar_MAVLINK_autopilot/CMakeLists.txt1-63

No external dependencies beyond Qt5:

The build process:

`mainwindow.ui`

file with Qt's UIC examples/map_local_twocars/CMakeLists.txt7`map_local_twocars`

Sources: examples/map_local_twocars/CMakeLists.txt1-60

The `map_local_twocars`

example is the easiest to start with as it requires no hardware or external systems.

**Launch**:

**What You'll See**:

`CarState`

vehicles**Basic Interaction**:

For detailed map visualization features, see Map Visualization System. For route planning, see Route Planning Interface.

Sources: examples/map_local_twocars/CMakeLists.txt26-29

**Prerequisites**:

**Launch**:

**Connection Setup**:

**System Integration**:

For MAVLink protocol details, see Vehicle Server (MavsdkVehicleServer). For autopilot configuration, see Pure Pursuit Waypoint Follower.

Sources: examples/RCCar_MAVLINK_autopilot/CMakeLists.txt26-62

Similar to MAVLink version but uses ISO 22133 protocol:

**Launch**:

**Connection Setup**:

`ISO_object`

library examples/RCCar_ISO22133_autopilot/CMakeLists.txt25-26Sources: examples/RCCar_ISO22133_autopilot/CMakeLists.txt28-63

WayWise uses XML-based route files. The `routeutils`

module provides file I/O:

**Route File Format**:

**Loading Routes**:
The `readRouteFromFile`

function handles coordinate transformation from the stored ENU reference to the vehicle's current ENU reference:

routeplanning/routeutils.cpp7-79

Key features:

For route generation tools, see Route Generation Tools. For coordinate systems, see Coordinate Systems & Transformations.

Sources: routeplanning/routeutils.h1-23 routeplanning/routeutils.cpp1-107

The `ZigZagRouteGenerator`

class provides algorithms for automated route creation:

**Available Patterns**:

`fillConvexPolygonWithZigZag()`

- Parallel passes within polygon bounds routeplanning/zigzagroutegenerator.h24-25`fillConvexPolygonWithFramedZigZag()`

- Perimeter frame followed by zigzag fill routeplanning/zigzagroutegenerator.h26-27**Key Parameters**:

| Parameter | Type | Purpose |
|---|---|---|
`bounds` | `QList<PosPoint>` | Convex polygon defining area |
`spacing` | `double` | Distance between parallel passes |
`keepTurnsInBounds` | `bool` | Ensure turn arcs stay within bounds |
`speed` | `double` | Speed on straight sections |
`speedInTurns` | `double` | Speed during turns |
`turnIntermediateSteps` | `int` | Number of waypoints per turn |
`visitEveryX` | `int` | Pattern for skipping passes |

**Algorithm Overview**:

Sources: routeplanning/zigzagroutegenerator.h1-36 routeplanning/zigzagroutegenerator.cpp141-165 routeplanning/zigzagroutegenerator.cpp167-392

The `isPointWithin`

function determines if a point lies within a polygon route:

routeplanning/routeutils.cpp81-107

Implementation uses ray casting algorithm:

**Usage**: Speed limit regions, geofencing, route validation.

For geofenced speed control, see Speed Limit Regions.

Sources: routeplanning/routeutils.h20-21 routeplanning/routeutils.cpp81-107

**Error**:

```
CMake Error at CMakeLists.txt:22 (find_package):
Could not find a package configuration file provided by "MAVSDK"
```


**Solution**: Install MAVSDK system-wide or set `MAVSDK_DIR`

:

**Error**:

```
CMake Error: Could not find Qt5SerialPort
```


**Solution**: Install Qt5 development packages:

**Error**:

```
CMake Error: The C++ compiler does not support C++17
```


**Solution**: Update compiler or specify newer compiler:

Sources: examples/RCCar_MAVLINK_autopilot/CMakeLists.txt11-22 examples/RCCar_ISO22133_autopilot/CMakeLists.txt11-22

After successfully building and running an example:

For system architecture overview, return to Architecture & System Design.

Refresh this wiki
