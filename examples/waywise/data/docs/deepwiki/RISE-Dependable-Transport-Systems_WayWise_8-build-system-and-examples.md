# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/8-build-system-and-examples

This page documents the CMake-based build system used by WayWise and provides detailed build instructions for the three example applications included in the `/examples`

directory. These examples demonstrate different deployment scenarios and communication protocols, serving as templates for building custom WayWise applications.

The three example applications covered are:

**Sources:** examples/RCCar_ISO22133_autopilot/CMakeLists.txt1-64 examples/RCCar_MAVLINK_autopilot/CMakeLists.txt1-63 examples/map_local_twocars/CMakeLists.txt1-60

WayWise uses CMake as its build system with a modular source file inclusion pattern. Applications do not link against a precompiled WayWise library; instead, they selectively include WayWise source files directly into their build based on required functionality.

All example applications define a `WAYWISE_PATH`

variable pointing to the WayWise repository root:

This variable enables relative path references for including WayWise source files and headers. The path is configured as `../..`

because example applications are located in `examples/<application_name>/`

, making the WayWise root two directories up.

The `WAYWISE_PATH`

is used in two ways:

`.cpp`

files are added directly to the executable's source list using `${WAYWISE_PATH}/path/to/file.cpp`

`target_include_directories(target PRIVATE ${WAYWISE_PATH})`

This pattern allows applications to include only the WayWise components they need, minimizing compile time and binary size.

**Sources:** examples/RCCar_ISO22133_autopilot/CMakeLists.txt24-57 examples/RCCar_MAVLINK_autopilot/CMakeLists.txt24-56 examples/map_local_twocars/CMakeLists.txt23-53

All three examples use consistent CMake configuration:

| Setting | Value | Purpose |
|---|---|---|
`CMAKE_CXX_STANDARD` | 17 | C++ language standard |
`CMAKE_C_STANDARD` | 23 | C language standard |
`CMAKE_AUTOUIC` | ON | Automatic UI file compilation (Qt) |
`CMAKE_AUTOMOC` | ON | Automatic Meta-Object Compiler (Qt) |
`CMAKE_AUTORCC` | ON | Automatic Resource Compiler (Qt) |

Compiler warnings are enabled for GCC and Clang:

**Sources:** examples/RCCar_ISO22133_autopilot/CMakeLists.txt7-19 examples/RCCar_MAVLINK_autopilot/CMakeLists.txt7-19 examples/map_local_twocars/CMakeLists.txt7-19

The `/examples`

directory contains three applications demonstrating different aspects of WayWise:

| Application | Purpose | Communication | Qt Components | Visualization |
|---|---|---|---|---|
`RCCar_ISO22133_autopilot` | Vehicle-side autopilot | ISO/TS 22133 (TCP) | Core, Network, SerialPort | None (headless) |
`RCCar_MAVLINK_autopilot` | Vehicle-side autopilot | MAVLink (UDP) | Core, Network, SerialPort | None (headless) |
`map_local_twocars` | Simulated ground station | None (local simulation) | Widgets, Core, Network, PrintSupport | MapWidget with OSM tiles |

The two autopilot examples differ primarily in their communication layer:

| Aspect | ISO22133 Example | MAVLink Example |
|---|---|---|
Server Class | `iso22133VehicleServer` | `MavsdkVehicleServer` |
External Library | `ISO_object` (custom submodule) | `MAVSDK` (system library) |
Protocol | ISO/TS 22133 over TCP | MAVLink over UDP |
Parameter Server | `ParameterServer` only | `MavlinkParameterServer` + `ParameterServer` |
Compatible Ground Stations | ATOS | ControlTower, QGroundControl, Mission Planner |
Submodule Required | Yes (`isoObject/` ) | No |

**Sources:** examples/RCCar_ISO22133_autopilot/CMakeLists.txt25-51 examples/RCCar_MAVLINK_autopilot/CMakeLists.txt44-50

Vehicle-side autopilot example demonstrating ISO/TS 22133 protocol integration. This example simulates an Ackermann-steered vehicle that accepts commands from ATOS or other ISO22133-compatible ground stations.

**Component Architecture Diagram**

**Sources:** examples/RCCar_ISO22133_autopilot/CMakeLists.txt28-55

**Required System Libraries:**

**External Library:**

`ISO_object`

- Custom library for ISO/TS 22133 protocol (included as git submodule in `isoObject/`

directory)**Sources:** examples/RCCar_ISO22133_autopilot/CMakeLists.txt21-26 examples/RCCar_ISO22133_autopilot/CMakeLists.txt59-63

The CMakeLists.txt includes 23 WayWise source files organized by subsystem:

| Subsystem | Files Included | Purpose |
|---|---|---|
Core | `simplewatchdog.cpp` , `vbytearray.cpp` , `pospoint.cpp` | Watchdog monitoring, byte arrays, position points |
Vehicle State | `objectstate.cpp` , `carstate.cpp` , `vehiclestate.cpp` | State hierarchy and kinematics |
Control | `movementcontroller.cpp` , `carmovementcontroller.cpp` , `servocontroller.cpp` , `motorcontroller.h` | Movement and actuator control |
Autopilot | `purepursuitwaypointfollower.cpp` , `followpoint.cpp` , `waypointfollower.h` | Pure Pursuit algorithm |
Communication | `iso22133vehicleserver.cpp` , `vehicleconnection.cpp` , `parameterserver.cpp` , `vehicleserver.h` | ISO22133 protocol server |
Sensors | `ublox.cpp` , `rtcm3_simple.cpp` , `ubloxrover.cpp` , `gnssreceiver.cpp` | GNSS support (not actively used in simulation) |
Camera | `gimbal.h` | Camera gimbal interface header |
Logging | `logger.cpp` | Event logging |
Route Planning | `routeutils.cpp` , `routeutils.h` | Route file I/O |

**Sources:** examples/RCCar_ISO22133_autopilot/CMakeLists.txt28-55

The application listens on TCP port 30100 for ISO/TS 22133 connections from ATOS.

**Sources:** examples/RCCar_ISO22133_autopilot/CMakeLists.txt1-64

Vehicle-side autopilot example demonstrating MAVLink protocol integration via MAVSDK. This example simulates an Ackermann-steered vehicle compatible with ControlTower, QGroundControl, and Mission Planner.

**Component Architecture Diagram**

**Sources:** examples/RCCar_MAVLINK_autopilot/CMakeLists.txt26-54

**Required System Libraries:**

**Sources:** examples/RCCar_MAVLINK_autopilot/CMakeLists.txt21-22 examples/RCCar_MAVLINK_autopilot/CMakeLists.txt58-62

The CMakeLists.txt includes 24 WayWise source files (one more than ISO22133 example):

| Subsystem | Files Included | Difference from ISO22133 |
|---|---|---|
Core | `simplewatchdog.cpp` , `vbytearray.cpp` , `pospoint.cpp` | Same |
Vehicle State | `objectstate.cpp` , `carstate.cpp` , `vehiclestate.cpp` | Same |
Control | `movementcontroller.cpp` , `carmovementcontroller.cpp` , `servocontroller.cpp` , `motorcontroller.h` | Same |
Autopilot | `purepursuitwaypointfollower.cpp` , `followpoint.cpp` , `waypointfollower.h` | Same |
Communication | `mavsdkvehicleserver.cpp` , `vehicleconnection.cpp` , `parameterserver.cpp` , `mavlinkparameterserver.cpp` , `vehicleserver.h` | Uses `mavsdkvehicleserver.cpp` + adds `mavlinkparameterserver.cpp` |
Sensors | `ublox.cpp` , `rtcm3_simple.cpp` , `ubloxrover.cpp` , `gnssreceiver.cpp` | Same |
Camera | `gimbal.h` | Same |
Logging | `logger.cpp` | Same |
Route Planning | `routeutils.cpp` , `routeutils.h` | Same |

The key difference is the communication layer:

`iso22133vehicleserver.cpp`

`mavsdkvehicleserver.cpp`

+ `mavlinkparameterserver.cpp`

**Sources:** examples/RCCar_MAVLINK_autopilot/CMakeLists.txt26-54

The application broadcasts MAVLink heartbeats on UDP port 14540 for ground station discovery.

**Sources:** examples/RCCar_MAVLINK_autopilot/CMakeLists.txt1-63

Ground station simulation example demonstrating local vehicle control with map visualization. This example simulates two `CarState`

vehicles in a single application with an interactive map display using OpenStreetMap tiles.

**Component Architecture Diagram**

**Sources:** examples/map_local_twocars/CMakeLists.txt25-51

**Required System Libraries:**

**Notable Absence:**

**Sources:** examples/map_local_twocars/CMakeLists.txt21-59

The CMakeLists.txt includes 21 WayWise source files with emphasis on visualization:

| Subsystem | Files Included | Purpose |
|---|---|---|
Vehicle State | `objectstate.cpp` , `vehiclestate.cpp` , `carstate.cpp` | Two-vehicle state management |
Control | `movementcontroller.cpp` , `carmovementcontroller.cpp` , `servocontroller.cpp` , `motorcontroller.h` | Movement control for both vehicles |
Autopilot | `purepursuitwaypointfollower.cpp` , `followpoint.cpp` , `waypointfollower.h` | Autopilot for waypoint following |
Map Visualization | `mapwidget.cpp` , `osmclient.cpp` , `osmtile.cpp` | OpenStreetMap rendering |
Communication | `vehicleconnection.cpp` , `parameterserver.cpp` | Abstract vehicle connection (no concrete server) |
Camera | `gimbal.h` | Camera interface header |
Route Planning | `routeutils.cpp` , `routeutils.h` | Route file I/O |
Core | `pospoint.cpp` , `coordinatetransforms.h` | Position points and coordinate math |

**Key Difference:** Includes map visualization components (`mapwidget.cpp`

, `osmclient.cpp`

, `osmtile.cpp`

) not present in autopilot examples.

**Sources:** examples/map_local_twocars/CMakeLists.txt25-51

The application opens a window with an interactive map displaying both simulated vehicles.

**Sources:** examples/map_local_twocars/CMakeLists.txt1-60

All three examples follow consistent patterns for including WayWise components:

**Diagram: WayWise Source File Categories**

**Sources:** examples/RCCar_ISO22133_autopilot/CMakeLists.txt28-55 examples/RCCar_MAVLINK_autopilot/CMakeLists.txt26-54 examples/map_local_twocars/CMakeLists.txt25-51

This table shows which source categories are included in each example:

| Category | ISO22133 | MAVLink | map_local_twocars |
|---|---|---|---|
| Core Utilities | ✓ | ✓ | ✓ (partial) |
| Vehicle State | ✓ | ✓ | ✓ |
| Control System | ✓ | ✓ | ✓ |
| Autopilot | ✓ | ✓ | ✓ |
| Communication | ✓ (ISO22133) | ✓ (MAVLink) | ✓ (abstract only) |
| Map & UI | ✗ | ✗ | ✓ |
| Sensors | ✓ (unused) | ✓ (unused) | ✗ |
| Route Planning | ✓ | ✓ | ✓ |
| Camera | ✓ (header) | ✓ (header) | ✓ (header) |
| Logging | ✓ | ✓ | ✗ |

**Sources:** examples/RCCar_ISO22133_autopilot/CMakeLists.txt28-55 examples/RCCar_MAVLINK_autopilot/CMakeLists.txt26-54 examples/map_local_twocars/CMakeLists.txt25-51

All source files use the `${WAYWISE_PATH}`

variable for relative path construction:

This pattern enables:

**Sources:** examples/RCCar_ISO22133_autopilot/CMakeLists.txt28-55

Both minimal example applications share a common set of dependencies and build patterns:

| Library | Purpose | MAVLink Example | ISO22133 Example |
|---|---|---|---|
`Qt5::Core` | Application framework | ✓ | ✓ |
`Qt5::Network` | Network communication | ✓ | ✓ |
`Qt5::SerialPort` | Hardware communication | ✓ | ✓ |
`MAVSDK::mavsdk` | MAVLink protocol | ✓ | ✗ |
`ISO_object` | ISO/TS 22133 protocol | ✗ | ✓ |

Both minimal examples compile identical WayWise source files, demonstrating the core subsystems:

| Subsystem | Source Files | Purpose |
|---|---|---|
Core | `simplewatchdog.cpp` , `vbytearray.cpp` , `pospoint.cpp` | Performance monitoring, byte utilities, position data structures |
Vehicle State | `objectstate.cpp` , `carstate.cpp` , `vehiclestate.cpp` | Vehicle state hierarchy and kinematic simulation |
Control | `carmovementcontroller.cpp` , `movementcontroller.cpp` , `servocontroller.cpp` | Movement control abstraction and actuator interface |
Communication | `vehicleconnection.cpp` , `parameterserver.cpp` | Vehicle connection abstraction and parameter management |
Autopilot | `purepursuitwaypointfollower.cpp` , `followpoint.cpp` | Pure Pursuit algorithm and point following |
Sensors | `ublox.cpp` , `ubloxrover.cpp` , `gnssreceiver.cpp` , `rtcm3_simple.cpp` | GNSS receiver support and RTK corrections |
Logging | `logger.cpp` | Event and message logging |

**Sources:** examples/RCCar_MAVLINK_autopilot/CMakeLists.txt26-52 examples/RCCar_ISO22133_autopilot/CMakeLists.txt28-53

Both examples use identical timing configuration:

`PosType::fused`

Standard autopilot settings across examples:

`setRepeatRoute(false)`

)`CarMovementController`

**Sources:** examples/RCCar_ISO22133_autopilot/main.cpp15-32

Both examples require identical system dependencies:

For the ISO22133 example, additional boost libraries are required:

Each example follows standard CMake build patterns:

The ISO22133 example additionally requires submodule initialization:

Refresh this wiki
