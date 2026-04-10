# Source: https://deepwiki.com/das-rise/WayWise/6.4-parameter-server

The Parameter Server subsystem provides a centralized mechanism for managing vehicle configuration and tuning values. It allows different components (such as movement controllers, autopilots, and sensor drivers) to register variables that can be read, modified, and persisted. The system supports a base singleton for internal management and a MAVLink-specific implementation for remote tuning via Ground Control Stations (GCS) using the `PARAM_REQUEST_LIST`

and `PARAM_SET`

protocols.

The `ParameterServer`

class is implemented as a singleton that manages mappings between string-based parameter names and functional bindings to class member variables communication/parameterserver.h14-15 It acts as the central repository for all tunable parameters within the WayWise ecosystem.

The server handles three primary types of parameters defined in `communication/parameterserver.h`

:

Instead of storing values directly, the `ParameterServer`

stores pairs of `std::function`

objects (getters and setters). This ensures that when a parameter is updated via the server, the change is immediately reflected in the owning object without manual polling communication/parameterserver.h50-51

| Function | Description |
|---|---|
`provideIntParameter` | Registers an integer parameter with a setter and getter binding communication/parameterserver.cpp55-59 |
`provideFloatParameter` | Registers a float parameter with a setter and getter binding communication/parameterserver.cpp61-65 |
`updateIntParameter` | Updates a registered integer parameter and triggers its setter communication/parameterserver.cpp29-40 |
`updateFloatParameter` | Updates a registered float parameter and triggers its setter communication/parameterserver.cpp42-53 |

The server can persist the current state of all registered parameters to an XML file. This is used to save configurations across reboots. The `saveParametersToXmlFile`

function iterates through all mappings, calls the getters to retrieve current values, and writes them to the specified path using `QXmlStreamWriter`

communication/parameterserver.cpp67-97

**Sources:** communication/parameterserver.h1-55 communication/parameterserver.cpp1-119

The `MavlinkParameterServer`

extends the base `ParameterServer`

to bridge internal parameters to the MAVLink protocol via the MAVSDK `ParamServer`

plugin communication/mavlinkparameterserver.h14-15 This allows any MAVLink-compatible software (like QGroundControl) to view and edit vehicle parameters.

`mavsdk::ParamServer`

object communication/mavlinkparameterserver.h28`CAL_ACC0_ID`

, `CAL_GYRO0_ID`

, and `SYS_HITL`

communication/mavlinkparameterserver.cpp16-20`provideIntParameter`

and `provideFloatParameter`

to simultaneously register the parameter in the local map and the MAVSDK `ParamServer`

plugin communication/mavlinkparameterserver.cpp37-49By convention, parameters should share a meaningful string prefix followed by an underscore (e.g., `PP_LOOKAHEAD`

). MAVLink imposes a strict limit of **16 ASCII characters** for parameter names communication/mavlinkparameterserver.cpp31-36

**Sources:** communication/mavlinkparameterserver.h1-32 communication/mavlinkparameterserver.cpp1-81

The codebase uses a consistent pattern where classes implementing `provideParametersToParameterServer()`

register their internal variables during initialization.

The following diagram illustrates how a vehicle component (like an Autopilot) connects its internal variables to the `ParameterServer`

and subsequently to a MAVLink GCS.

**Logic to Code Entity Mapping: Parameter Binding**

**Sources:** communication/parameterserver.h50-51 communication/mavlinkparameterserver.cpp44-49 communication/parameterserver.cpp67-70

When a parameter is updated from an external source (like a MAVLink `PARAM_SET`

message), the flow proceeds through the functional bindings.

**System Sequence: External Parameter Update**

**Sources:** communication/parameterserver.cpp42-53 communication/mavlinkparameterserver.cpp44-49 communication/parameterserver.h51

The `ParameterServer`

uses a static initialization pattern to ensure the singleton instance is correctly typed (either base or Mavlink-enabled) before any components attempt to register parameters.

| Method | Role |
|---|---|
`ParameterServer::initialize()` | Creates a standard `ParameterServer` instance communication/parameterserver.cpp14-20 |
`MavlinkParameterServer::initialize(serverComponent)` | Creates a `MavlinkParameterServer` instance and links it to the MAVSDK server communication/mavlinkparameterserver.cpp23-29 |
`ParameterServer::getInstance()` | Returns the active singleton pointer communication/parameterserver.cpp22-27 |

**Sources:** communication/parameterserver.cpp10-27 communication/mavlinkparameterserver.cpp23-29

Refresh this wiki

This wiki was recently refreshed. Please wait 7 days to refresh again.