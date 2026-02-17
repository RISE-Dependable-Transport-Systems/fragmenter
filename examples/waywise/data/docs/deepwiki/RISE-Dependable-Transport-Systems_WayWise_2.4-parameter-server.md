# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/2.4-parameter-server

The Parameter Server is a configuration management system that enables runtime parameter exchange between ground station and vehicle components in WayWise. It provides a centralized registry where components can register parameters with getter/setter callbacks, supporting both local (ground station) and remote (vehicle-side) parameter modification. Parameters are synchronized over MAVLink using the standard PARAM_VALUE message protocol.

For information about the vehicle-side MAVLink interface that uses ParameterServer, see Vehicle Server (MavsdkVehicleServer). For the ground-station UI that displays and modifies parameters, see Parameter Configuration UI.

The Parameter Server operates in two deployment contexts: on the ground station (control tower) and on the vehicle. Both contexts use the same `ParameterServer`

singleton pattern, but the vehicle additionally uses `MavlinkParameterServer`

to synchronize parameters over MAVLink.

**Sources:** communication/mavsdkvehicleserver.cpp36-37 communication/mavsdkvehicleserver.cpp441-451 userinterface/vehicleparameterui.cpp27-32

Components register parameters by calling `provideFloatParameter()`

, `provideIntParameter()`

, or `provideCustomParameter()`

on the `ParameterServer::getInstance()`

singleton. Each registration binds a parameter name to a getter function and a setter function using `std::function`

callbacks.

| Method | Signature | Parameter Type |
|---|---|---|
`provideFloatParameter()` | `void provideFloatParameter(const char* name, std::function<void(float)> setter, std::function<float(void)> getter)` | `float` |
`provideIntParameter()` | `void provideIntParameter(const char* name, std::function<void(int)> setter, std::function<int(void)> getter)` | `int32_t` |
`provideCustomParameter()` | `void provideCustomParameter(const char* name, std::function<void(std::string)> setter, std::function<std::string(void)> getter)` | `std::string` |

The Pure Pursuit autopilot registers two parameters to control its behavior at runtime:

```
PP_RADIUS - Pure pursuit lookahead radius (meters)
PP_ARC - Adaptive radius coefficient (speed multiplier)
```


Registration occurs in `PurepursuitWaypointFollower::provideParametersToParameterServer()`

using `std::bind`

to connect parameter callbacks to class member functions:

autopilot/purepursuitwaypointfollower.cpp31-37

**Sources:** autopilot/purepursuitwaypointfollower.cpp31-37

The vehicle server registers vehicle-wide parameters, including manual control speed limits:

```
MC_MAX_SPEED_MS - Manual control maximum speed (m/s)
VEH_WW_OBJ_TYPE - WayWise object type enumeration
```


Registration occurs in `MavsdkVehicleServer::provideParametersToParameterServer()`

using lambda functions and `std::bind`

:

communication/mavsdkvehicleserver.cpp481-487

**Sources:** communication/mavsdkvehicleserver.cpp481-487

Parameters are internally stored in three separate containers within `ParameterServer`

, one for each type. Each parameter entry includes the name, current value, and callback functions.

All parameters can be retrieved as a single structure using `ParameterServer::getAllParameters()`

, which returns a `ParameterServer::AllParameters`

struct containing vectors of all three parameter types.

**Sources:** userinterface/vehicleparameterui.cpp39-40

On the vehicle side, `MavlinkParameterServer`

extends `ParameterServer`

to integrate with MAVSDK's parameter protocol. It is initialized as a singleton using `MavlinkParameterServer::initialize(serverComponent)`

, where `serverComponent`

is a MAVSDK server component instance.

**Sources:** communication/mavsdkvehicleserver.cpp33-37

When MAVLink `PARAM_VALUE`

messages are received (typically after a parameter set operation), `MavsdkVehicleServer`

intercepts them and updates the parameter server. The message is decoded to extract parameter name, value, and type, then the appropriate update method is called:

communication/mavsdkvehicleserver.cpp441-451

The update distinguishes between float and integer parameters based on `param_type`

:

`MAV_PARAM_TYPE_REAL32`

→ calls `updateFloatParameter()`

`MAV_PARAM_TYPE_INT32`

→ calls `updateIntParameter()`

after converting from `param_union_t`

**Sources:** communication/mavsdkvehicleserver.cpp441-451

When a parameter value is updated (either locally or via MAVLink), the ParameterServer calls the registered setter function, which propagates the change to the owning component. The setter function is responsible for applying the new value to the component's internal state.

On the ground station side, `VehicleParameterUI`

detects changed values in the table widget and calls `VehicleConnection::setFloatParameterOnVehicle()`

or `VehicleConnection::setIntParameterOnVehicle()`

, which sends MAVLink parameter set commands to the vehicle:

userinterface/vehicleparameterui.cpp126-134

The vehicle's `MavsdkVehicleServer`

intercepts outgoing `PARAM_VALUE`

messages and calls `MavlinkParameterServer::updateFloatParameter()`

or `updateIntParameter()`

to ensure the ParameterServer's internal cache remains synchronized with MAVLink messages.

**Sources:** userinterface/vehicleparameterui.cpp98-173 communication/mavsdkvehicleserver.cpp441-451

`VehicleParameterUI`

provides a table-based interface for viewing and modifying parameters. It retrieves parameters from two sources:

`VehicleConnection::getAllParametersFromVehicle()`

, which queries the vehicle over MAVLink`ParameterServer::getInstance()->getAllParameters()`

, which queries the local ground station instanceThe UI displays all parameters in rows with two columns:

When the user clicks "Set New Parameters On Vehicle", the UI iterates through all rows, compares the table values with cached values, and sends updates only for changed parameters:

userinterface/vehicleparameterui.cpp98-173

**Sources:** userinterface/vehicleparameterui.cpp27-32 userinterface/vehicleparameterui.cpp35-95 userinterface/vehicleparameterui.cpp98-173

Parameters follow a structured naming convention to indicate their scope and purpose:

| Prefix | Scope | Examples |
|---|---|---|
`PP_` | Pure Pursuit autopilot | `PP_RADIUS` , `PP_ARC` |
`MC_` | Manual control | `MC_MAX_SPEED_MS` |
`VEH_` | Vehicle-wide settings | `VEH_WW_OBJ_TYPE` |

This naming convention helps organize parameters when displayed in the VehicleParameterUI table and makes it easier to identify which component owns each parameter.

**Sources:** autopilot/purepursuitwaypointfollower.cpp34-35 communication/mavsdkvehicleserver.cpp482-486

Components that wish to expose configurable parameters follow this pattern:

`provideParametersToParameterServer()`

method`provideParametersToParameterServer()`

This callback-based design decouples the parameter management system from component implementations, allowing parameters to be added or modified without changing the ParameterServer infrastructure.

**Sources:** autopilot/purepursuitwaypointfollower.cpp31-37 communication/mavsdkvehicleserver.cpp481-487

Refresh this wiki
