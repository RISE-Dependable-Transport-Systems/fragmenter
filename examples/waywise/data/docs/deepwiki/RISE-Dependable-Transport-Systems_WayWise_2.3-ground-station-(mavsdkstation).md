# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/2.3-ground-station-(mavsdkstation)

`MavsdkStation`

is the ground control station component that manages MAVLink communication with multiple vehicles. It acts as a connection hub that listens for incoming MAVLink connections (UDP or serial), automatically discovers vehicles, monitors their health via heartbeats, and broadcasts shared data such as RTCM corrections and ENU reference frames to all connected vehicles.

For information about individual vehicle connections managed by this station, see Vehicle Connection. For the vehicle-side MAVLink server, see Vehicle Server.

**Sources:** communication/vehicleconnections/mavsdkstation.h1-56 communication/vehicleconnections/mavsdkstation.cpp1-132

`MavsdkStation`

extends `QObject`

and encapsulates a MAVSDK instance configured as a ground station. It maintains a map of connected vehicles and provides methods for connection management, vehicle discovery, and data broadcasting.

**Sources:** communication/vehicleconnections/mavsdkstation.h22-54 communication/vehicleconnections/mavsdkstation.cpp9-21

The `MavsdkStation`

constructor initializes the MAVSDK instance with ground station configuration and sets up the heartbeat monitoring system.

**Key configuration details:**

`mavsdk::Mavsdk::ComponentType::GroundStation`

`true`

`HEARTBEATTIMER_TIMEOUT_SECONDS`

)**Sources:** communication/vehicleconnections/mavsdkstation.cpp9-21 communication/vehicleconnections/mavsdkstation.h47-52

The `startListeningUDP()`

method configures MAVSDK to listen for MAVLink messages on a UDP port.

| Parameter | Type | Default | Description |
|---|---|---|---|
`port` | `uint16_t` | `mavsdk::Mavsdk::DEFAULT_UDP_PORT` (14540) | UDP port to bind |

**Returns:** `bool`

- `true`

if connection established successfully, `false`

otherwise

**Implementation:**

```
connection_url = "udp://:" + port
mMavsdk->add_any_connection(connection_url)
```


**Sources:** communication/vehicleconnections/mavsdkstation.cpp23-34 communication/vehicleconnections/mavsdkstation.h27

The `startListeningSerial()`

method configures MAVSDK to communicate over a serial port (e.g., radio telemetry, direct cable).

| Parameter | Type | Default | Description |
|---|---|---|---|
`portInfo` | `QSerialPortInfo` | "ttyUSB0" | Serial port information |
`baudrate` | `int` | `mavsdk::Mavsdk::DEFAULT_SERIAL_BAUDRATE` (57600) | Serial baudrate |

**Returns:** `bool`

- `true`

if connection opened successfully, `false`

otherwise

**Implementation:**

```
mMavsdk->add_serial_connection(portInfo.systemLocation(), baudrate)
```


**Sources:** communication/vehicleconnections/mavsdkstation.cpp36-46 communication/vehicleconnections/mavsdkstation.h28

The `SerialPortDialog`

class provides a UI for selecting serial ports and baudrates when establishing serial connections.

The dialog displays available serial ports with manufacturer and description information, and provides a combo box for standard baudrate selection (default: 57600).

**Sources:** userinterface/serialportdialog.h1-39 userinterface/serialportdialog.cpp1-59 userinterface/serialportdialog.ui1-96

When MAVSDK detects a new MAVLink system, it triggers a multi-stage initialization process:

**Key steps:**

`subscribe_on_new_system()`

`Qt::QueuedConnection`

`system->has_autopilot()`

`nullptr`

placeholder`MavlinkPassthrough`

to wait for first heartbeat`MAV_TYPE`

from heartbeat message`MavsdkVehicleConnection`

with correct type`gotNewVehicleConnection`

signal**Sources:** communication/vehicleconnections/mavsdkstation.cpp98-131 communication/vehicleconnections/mavsdkstation.cpp18-20

The system waits for a heartbeat message before fully initializing the vehicle connection because:

`MAV_TYPE`

field (e.g., `MAV_TYPE_GROUND_ROVER`

, `MAV_TYPE_QUADROTOR`

)`MavsdkVehicleConnection`

constructor requires the vehicle type to set up appropriate plugins**Sources:** communication/vehicleconnections/mavsdkstation.cpp102-127

`MavsdkStation`

monitors vehicle connection health using a 1Hz timer and per-vehicle timeout counters.

The `on_timeout()`

method runs every 1000ms and increments all vehicle counters:

| Timeout Counter | Action |
|---|---|
| 0-4 seconds | Increment counter, no action |
| 5 seconds | Remove from `mVehicleConnectionMap` , emit `disconnectOfVehicleConnection` , delete counter |

**Sources:** communication/vehicleconnections/mavsdkstation.cpp70-84

When a vehicle sends a heartbeat (detected by `MavsdkVehicleConnection`

), it emits `gotHeartbeat(systemId)`

, which triggers `on_gotHeartbeat()`

:

**Sources:** communication/vehicleconnections/mavsdkstation.cpp86-91 communication/vehicleconnections/mavsdkstation.cpp120

The `forwardRtcmData()`

method broadcasts RTCM correction data to all connected vehicles, enabling RTK positioning.

**Method signature:**

**Implementation:**

**Sources:** communication/vehicleconnections/mavsdkstation.cpp48-53 communication/vehicleconnections/mavsdkstation.h31

The `setEnuReference()`

method sets the ENU (East-North-Up) coordinate reference point for all vehicles.

**Method signature:**

**Implementation:**

**Sources:** communication/vehicleconnections/mavsdkstation.cpp55-59 communication/vehicleconnections/mavsdkstation.h32

The `getVehicleConnectionList()`

method returns a list of all active vehicle connections, filtering out `nullptr`

entries.

**Method signature:**

**Returns:** List of active vehicle connections (excludes nullptrs from initial registration phase)

**Sources:** communication/vehicleconnections/mavsdkstation.cpp61-68 communication/vehicleconnections/mavsdkstation.h34

The `getVehicleConnection()`

method retrieves a specific vehicle connection by system ID.

**Method signature:**

**Parameters:**

`systemId`

: MAVLink system ID (1-255)**Returns:** Shared pointer to vehicle connection, or `nullptr`

if not found

**Sources:** communication/vehicleconnections/mavsdkstation.cpp93-96 communication/vehicleconnections/mavsdkstation.h35

```
QMap<int, QSharedPointer<MavsdkVehicleConnection>> mVehicleConnectionMap
```


`MavsdkVehicleConnection`

(or `nullptr`

during initialization)**Lifecycle:**

`(systemId, nullptr)`

`MavsdkVehicleConnection`

**Sources:** communication/vehicleconnections/mavsdkstation.h48

```
QVector<QPair<quint8, int>> mVehicleHeartbeatTimeoutCounters
```


`quint8`

)**Updated by:**

`on_timeout()`

: Increments all counters every 1 second`on_gotHeartbeat()`

: Resets specific counter to 0**Sources:** communication/vehicleconnections/mavsdkstation.h52

Emitted when a new vehicle has been fully initialized and is ready for use. Applications should connect to this signal to update UI or register the vehicle.

**Sources:** communication/vehicleconnections/mavsdkstation.h42 communication/vehicleconnections/mavsdkstation.cpp124

Internal signal emitted when MAVSDK detects a new system. Connected to `handleNewMavsdkSystem()`

slot via `Qt::QueuedConnection`

to ensure thread safety.

**Sources:** communication/vehicleconnections/mavsdkstation.h43 communication/vehicleconnections/mavsdkstation.cpp18

Emitted when a vehicle times out after 5 seconds without heartbeats. Applications should remove the vehicle from UI and clean up resources.

**Sources:** communication/vehicleconnections/mavsdkstation.h44 communication/vehicleconnections/mavsdkstation.cpp77

The `gotNewMavsdkSystem`

signal uses `Qt::QueuedConnection`

when connecting to `handleNewMavsdkSystem()`

:

This ensures that system discovery callbacks from MAVSDK's internal threads are safely handled on the `MavsdkStation`

object's thread (typically the main Qt event loop).

**Sources:** communication/vehicleconnections/mavsdkstation.cpp20

**Sources:** communication/vehicleconnections/mavsdkstation.h1-56 communication/vehicleconnections/mavsdkstation.cpp1-132

Refresh this wiki
