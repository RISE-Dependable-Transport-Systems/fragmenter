# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/6.6-parameter-configuration-ui

The Parameter Configuration UI (`VehicleParameterUI`

) provides a graphical interface for viewing and modifying runtime parameters on both remote vehicles and the local ground control station. This system enables bidirectional parameter synchronization, allowing operators to retrieve parameter values from connected vehicles and update them as needed during operations.

For information about the underlying parameter storage and MAVLink integration, see Parameter Server. For vehicle-specific control interfaces, see Ground Vehicle Control and Drone Flight Control.

`VehicleParameterUI`

is a Qt dialog that connects to two parameter sources simultaneously:

`VehicleConnection`

interface`ParameterServer`

singletonThe UI displays all parameters in an editable table, detects changes, and synchronizes modified values back to their respective sources. This dual-source approach allows configuration of both onboard vehicle systems and ground station autopilot settings from a single interface.

**Sources:** userinterface/vehicleparameterui.h1-43 userinterface/vehicleparameterui.cpp1-174

**Diagram: Component Architecture**

The dialog operates as an intermediary between the UI table and two parameter backends. Parameter retrieval and modification flow through dedicated methods on `VehicleConnection`

and `ParameterServer`

.

**Sources:** userinterface/vehicleparameterui.h18-42 userinterface/vehicleparameterui.cpp22-173

Vehicle parameters are retrieved from the connected vehicle's onboard system via MAVLink parameter protocol. Three parameter types are supported:

| Parameter Type | Data Type | Example Use Case |
|---|---|---|
| Integer | `int32_t` | Enumeration values, counts, IDs |
| Float | `float` | Physical constants, gains, thresholds |
| Custom | `std::string` | Text-based configuration, file paths |

Vehicle parameters are accessed through the `VehicleConnection`

interface:

`getAllParametersFromVehicle()`

returns a `ParameterServer::AllParameters`

struct vehicleparameterui.cpp30Control tower (ground station) parameters are stored locally in the `ParameterServer`

singleton and persisted to XML. These parameters configure the ground-based autopilot systems, UI behavior, and communication settings.

Control tower parameters support:

`updateIntParameter()`

vehicleparameterui.cpp152`updateFloatParameter()`

vehicleparameterui.cpp163**Sources:** userinterface/vehicleparameterui.cpp28-95

The UI consists of three primary elements defined in userinterface/vehicleparameterui.ui1-218:

**Diagram: UI Component Hierarchy**

The `QTableWidget`

is configured with:

**Sources:** userinterface/vehicleparameterui.ui25-194

**Diagram: Parameter Retrieval Flow**

The retrieval process follows this sequence vehicleparameterui.cpp27-95:

`getAllParametersFromVehicle()`

on the current vehicle connection`ParameterServer::getInstance()->getAllParameters()`

`std::setprecision(6)`

vehicleparameterui.cpp57-65**Sources:** userinterface/vehicleparameterui.cpp27-95

**Diagram: Parameter Update Flow**

The update process vehicleparameterui.cpp108-173:

`ParameterServer`

`false`

immediately if any parameter update fails vehicleparameterui.cpp119-145**Sources:** userinterface/vehicleparameterui.cpp97-173

The `VehicleParameterUI`

is instantiated and managed by `DriveUI`

(ground vehicle control interface):

| Integration Point | Implementation |
|---|---|
| Instantiation | Lazy creation via `QSharedPointer` on first use driveui.cpp181-182 |
| Vehicle Binding | `setCurrentVehicleConnection()` called before showing driveui.cpp183 |
| Keyboard Handling | `DriveUI` releases keyboard grab when showing dialog driveui.cpp185 |
| Storage | `mVehicleParameterUI` member variable driveui.h53 |

The `releaseKeyboard()`

call is critical: `DriveUI`

captures keyboard events for manual vehicle control (arrow keys), but these would interfere with text input in the parameter table driveui.cpp185

**Sources:** userinterface/driveui.cpp179-186 userinterface/driveui.h53

Both vehicle and control tower parameters are stored using `ParameterServer::AllParameters`

:

Each parameter type has a corresponding structure with `name`

and `value`

fields vehicleparameterui.cpp48-145

| Parameter Type | Table Widget Conversion | Format |
|---|---|---|
| Integer | `text().toInt()` | Plain integer string |
| Float | `text().toFloat()` | 6 decimal places (display only) |
| Custom | `text().toStdString()` | UTF-8 string |

Float values use `std::setprecision(6)`

for display vehicleparameterui.cpp59 but Qt's `toFloat()`

parses any valid float format during updates.

**Sources:** userinterface/vehicleparameterui.h38-39 userinterface/vehicleparameterui.cpp48-168

The parameter update system uses different error handling strategies for each source:

Vehicle parameter updates return `VehicleConnection::Result`

enum:

`false`

, stopping further updates vehicleparameterui.cpp119-130This fail-fast approach prevents partial parameter updates that could leave the vehicle in an inconsistent state.

Control tower parameter updates return `bool`

:

`true`

from `ParameterServer::updateIntParameter()`

/ `updateFloatParameter()`

`false`

, immediately return from update function vehicleparameterui.cpp152-164The status label provides color-coded feedback vehicleparameterui.cpp99-105:

**Sources:** userinterface/vehicleparameterui.cpp97-173

Typical workflow for updating vehicle parameters:

`DriveUI`

driveui.ui62-72Parameters visible in the table use the naming conventions from both sources:

`MavlinkParameterServer`

(see Parameter Server)`ParameterServer`

XML configurationExample parameters might include:

`PP_RADIUS`

: Pure Pursuit look-ahead radius (control tower)`PP_ARC`

: Pure Pursuit arc fraction (control tower)**Sources:** userinterface/vehicleparameterui.cpp35-95

The UI operates on the main Qt thread. All `VehicleConnection`

and `ParameterServer`

calls are synchronous and blocking, ensuring parameter consistency during retrieval and updates.

`QSharedPointer`

in `DriveUI`

driveui.h53`QTableWidget`

, automatically deleted when table is cleared or destroyed`mVehicleParameters`

and `mControlTowerParameters`

vehicleparameterui.h38-39The table is not automatically refreshed when parameters change externally. Users must click "Get Parameters From Vehicle" again to see updated values from the vehicle or control tower.

**Sources:** userinterface/vehicleparameterui.h32-42 userinterface/vehicleparameterui.cpp35-95

Refresh this wiki
