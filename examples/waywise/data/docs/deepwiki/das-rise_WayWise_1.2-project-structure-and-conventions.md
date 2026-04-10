# Source: https://deepwiki.com/das-rise/WayWise/1.2-project-structure-and-conventions

This page details the organizational layout of the WayWise codebase, the architectural patterns employed across its subsystems, and the development conventions required for contributors. WayWise is built as a rapid prototyping library using **C++** and the **Qt Framework**, emphasizing modularity to support diverse vehicle types and communication protocols.

The repository is organized into functional modules that separate core logic, hardware interfacing, and user representation.

| Directory | Purpose | Key Responsibilities |
|---|---|---|
`core` | Foundational Utilities | Coordinate transforms (LLH/ENU), `PosPoint` data structures, and basic math. |
`communication` | External Interfacing | MAVLink/MAVSDK implementations, ISO 22133 support, and CANopen logic. |
`vehicles` | State Representation | Classes for `CarState` , `CopterState` , and `TruckState` including kinematics. |
`sensors` | Data Acquisition | Drivers for u-blox GNSS, BNO055 IMU, Pozyx UWB, and DepthAI cameras. |
`autopilot` | Path Execution | Implementations of `WaypointFollower` (e.g., Pure Pursuit). |
`userinterface` | UI Components | Qt-based building blocks like `MapWidget` , `DriveUI` , and `PlanUI` . |
`routeplanning` | Path Generation | Algorithms for zigzag patterns and polygon filling. |
`logger` | Data Persistence | Vehicle and ground station telemetry logging. |
`external` | Third-party Code | Vendored libraries (VESC, Fusion AHRS, AS5600 drivers). |
`tools` | Development Aids | Scripts for building MAVSDK and CI/CD helpers. |

**Sources:** README.md40-54 README.md14-17

WayWise relies heavily on the **Qt Object Model**. Developers must adhere to specific patterns regarding memory management and object communication to ensure stability in a multi-threaded environment.

The codebase prefers the use of `QSharedPointer`

for managing the lifecycle of vehicle states and connection objects. This prevents "use-after-free" errors when multiple UI components or background threads reference the same vehicle instance.

Communication between the "Brain" (autopilot/logic) and the "Body" (hardware/sensors) is handled via Qt's signal/slot mechanism.

`GNSSReceiver`

updates).`targetCurvature`

) which are connected to `MovementController`

implementations.Classes that require runtime configuration (like PID gains or look-ahead distances) must implement a pattern to provide their parameters to a central `ParameterServer`

. This allows MAVLink-based ground stations to modify vehicle behavior live.

**Sources:** README.md8-10 .github/CONTRIBUTING.md9-11

The following diagram maps the relationship between code entities across different directories during a standard autonomous mission.

**Diagram: WayWise Entity Interaction**

**Sources:** README.md40-49 README.md14-17

This diagram bridges the natural language concept of "Ground Control" and "Autonomous Vehicle" to specific code namespaces and classes.

**Diagram: Codebase Deployment Mapping**

**Sources:** README.md9-11 README.md14-17 README.md50-52

WayWise is released under the **GNU General Public License Version 3 (GPLv3)**. This is a copyleft license, meaning any derivative works must also be open-sourced under the same terms.

**Sources:** LICENSE1-11 LICENSE112-145

`waywise@ri.se`

.**Sources:** .github/SECURITY.md1-13 README.md12-13 README.md29-32

The project uses **CMake** as its primary build system. A GitHub Actions workflow is configured to verify builds for the library and its main examples on Ubuntu 22.04 and 24.04.

`qtbase5-dev`

, `libmavsdk-dev`

, and serial port libraries.`cmake --build`

for the `examples`

, `RCCar`

, and `ControlTower`

targets.**Sources:** .github/workflows/main.yml21-36 .github/workflows/main.yml74-95

Refresh this wiki

This wiki was recently refreshed. Please wait 7 days to refresh again.