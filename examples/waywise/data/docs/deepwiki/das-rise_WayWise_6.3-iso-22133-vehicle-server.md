# Source: https://deepwiki.com/das-rise/WayWise/6.3-iso-22133-vehicle-server

The `iso22133VehicleServer`

provides a standardized communication interface based on the ISO 22133 standard, specifically utilizing the RI-SE `isoObject`

library. It acts as a bridge between the WayWise internal vehicle state/autopilot systems and external test orchestration software. This server handles trajectory reception, telemetry reporting (MONR), and safety-critical commands like remote aborts.

The `iso22133VehicleServer`

employs multiple inheritance, deriving from the base `VehicleServer`

class and the `ISO22133::TestObject`

provided by the external RI-SE library communication/iso22133vehicleserver.h10-11

The following diagram illustrates how the `iso22133VehicleServer`

connects external ISO 22133 messages to internal WayWise components.

**ISO 22133 Data Flow**

**Sources:** communication/iso22133vehicleserver.cpp153-193 communication/iso22133vehicleserver.h10-11

When an `OSEM`

message is received, the server updates the local object settings and extracts the coordinate system origin. This origin is passed to the `VehicleState`

to set the ENU (East-North-Up) reference point, ensuring that subsequent local coordinates align with the global LLH coordinates provided by the orchestrator communication/iso22133vehicleserver.cpp159-169

The `onTRAJ`

function handles incoming mission profiles.

`isoObject`

library communication/iso22133vehicleserver.cpp175`WaypointFollower`

communication/iso22133vehicleserver.cpp182`TrajectoryWaypointType`

points into WayWise `PosPoint`

objects using `convertTrajPointToPosPoint`

communication/iso22133vehicleserver.cpp183-187The server maintains a high-frequency telemetry loop (defined by `MONR_RATE_MS`

, typically 10ms) communication/iso22133vehicleserver.cpp3

`fused`

position from `VehicleState`

communication/iso22133vehicleserver.cpp45-47`DriveDirectionType`

(Forward/Backward) communication/iso22133vehicleserver.cpp58-73**Sources:** communication/iso22133vehicleserver.cpp39-80 communication/iso22133vehicleserver.cpp171-193

The server implements strict safety protocols to ensure the vehicle stops in case of communication loss or explicit abort commands.

The `handleAbort()`

function is triggered by the ISO 22133 library. It immediately:

`setStopCommands()`

, which sends 0.0 speed and 0.0 steering to the `MovementController`

communication/iso22133vehicleserver.cpp136-140`WaypointFollower`

communication/iso22133vehicleserver.cpp132-134A `QTimer`

based heartbeat mechanism monitors the connection. If the heartbeat times out, `heartbeatTimeout()`

is invoked, executing the same `setStopCommands()`

safety routine as an abort communication/iso22133vehicleserver.cpp142-146

**Entity Mapping: Safety Logic**

**Sources:** communication/iso22133vehicleserver.cpp10-16 communication/iso22133vehicleserver.cpp131-157 communication/iso22133vehicleserver.h31-35

The `convertTrajPointToPosPoint`

function bridges the ISO 22133 data structures to WayWise internal types:

ISO 22133 Field (`TrajectoryWaypointType` ) | WayWise Field (`PosPoint` ) | Note |
|---|---|---|
`pos.xCoord_m` | `setX()` | Local ENU X |
`pos.yCoord_m` | `setY()` | Local ENU Y |
`pos.heading_rad` | `setYaw()` | Converted to degrees |
`speed_m_s` | `setSpeed()` | Target velocity |

**Sources:** communication/iso22133vehicleserver.cpp195-201

The implementation relies on the `isoObject`

external library, which is integrated as a git submodule .gitmodules1-4 This library provides the low-level socket handling and protocol parsing for the ISO 22133 standard.

**Sources:** .gitmodules1-4 communication/iso22133vehicleserver.h6

Refresh this wiki

This wiki was recently refreshed. Please wait 7 days to refresh again.