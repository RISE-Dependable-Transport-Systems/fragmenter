# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/7.1-coordinate-systems-and-transformations

This page explains the three coordinate systems used in WayWise and the transformations between them. Understanding these systems is critical for working with position data from sensors, map visualization, and vehicle control.

The three coordinate systems are:

For information about how position data is stored and tracked within vehicles, see Position Types & PosPoint Structure. For sensor fusion algorithms that process this coordinate data, see Sensor Fusion Algorithm.

**Data Structure**: `llh_t`

with fields `latitude`

, `longitude`

, `height`


LLH represents absolute global positions using the WGS-84 geodetic coordinate system. This is the native output format from GNSS receivers and is used for:

**Characteristics**:

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp94-105 sensors/gnss/ubloxrover.cpp351-387

**Data Structure**: `xyz_t`

with fields `x`

, `y`

, `z`

representing East, North, Up

ENU is a local Cartesian coordinate system with its origin at a specific LLH reference point (`mEnuReference`

or `mRefLlh`

). This is the primary working coordinate system in WayWise for:

**Characteristics**:

Sources: userinterface/map/mapwidget.cpp40-43 vehicles/vehiclestate.h

**Data Structure**: `xyz_t`

with fields `x`

, `y`

, `z`

representing North, East, Down

NED is used by flight controller firmware (e.g., PX4) and MAVLink telemetry. WayWise converts between NED and ENU when communicating with PX4-based vehicles.

**Characteristics**:

`POSITION_VELOCITY_NED`

messagesSources: communication/vehicleconnections/mavsdkvehicleconnection.cpp107-115 communication/vehicleconnections/mavsdkvehicleconnection.cpp137-141

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp83-147 sensors/gnss/gnssreceiver.cpp59-110 userinterface/map/mapwidget.cpp16-55 sensors/fusion/sdvpvehiclepositionfuser.cpp63-108

The ENU reference point is the origin of the local ENU coordinate system. It is stored as an LLH coordinate and is critical for coordinate transformations.

| Component | Variable Name | Type | Purpose |
|---|---|---|---|
`ObjectState` | `mEnuReference` | `llh_t` | ENU origin for this object's positions |
`MapWidget` | `mRefLlh` | `llh_t` | ENU origin for map visualization |
`MavsdkVehicleConnection` | `mEnuReference` | `llh_t` | ENU origin for vehicle communication |
`MavsdkVehicleConnection` | `mGpsGlobalOrigin` | `llh_t` | Vehicle's on-board EKF origin (NED frame) |

Sources: vehicles/objectstate.h userinterface/map/mapwidget.h125 communication/vehicleconnections/mavsdkvehicleconnection.h80-83

The ENU reference is typically set when the first GNSS position is received:

Sources: sensors/gnss/gnssreceiver.cpp65-67

**Important Considerations**:

The `MapWidget`

allows manual ENU reference changes via Ctrl+Shift+Left Click:

Sources: userinterface/map/mapwidget.cpp272-281

All transformation functions are in the `coordinateTransforms`

namespace (implementation not shown in provided files, but usage is extensive).

**Usage Example - GNSS Position Update**:

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp94-127 userinterface/map/mapwidget.cpp662-677

**Transformation Logic**:

**Usage Example - PX4 Telemetry**:

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp137-141 communication/vehicleconnections/mavsdkvehicleconnection.cpp562-563

Yaw angles require special handling because NED measures clockwise from North while ENU measures counter-clockwise from East.

**Usage Example - Heading Conversion**:

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp129-135 sensors/gnss/gnssreceiver.cpp75

WayWise handles coordinate systems differently based on vehicle type.

**Key Code**:

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp107-115

**Key Code**:

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp116-127 communication/vehicleconnections/mavsdkvehicleconnection.cpp514-546

The `SDVPVehiclePositionFuser`

operates entirely in ENU coordinates. It fuses GNSS, IMU, and odometry data to produce a high-rate, low-latency position estimate.

**No Coordinate Conversions**: The fuser assumes all inputs are already in ENU. Conversion from GNSS LLH to ENU happens earlier in the pipeline at `GNSSReceiver::updateGNSSPositionAndOrientation`

.

Sources: sensors/fusion/sdvpvehiclepositionfuser.cpp63-178 sensors/gnss/gnssreceiver.cpp59-104

The `MapWidget`

manages coordinate transformations for visualization, handling both ENU (for vehicle positions) and LLH (for OSM tiles).

**Drawing Workflow**:

**Key Transformation Code**:

Sources: userinterface/map/mapwidget.cpp658-727 userinterface/map/mapwidget.cpp272-281

Sensor offsets (lever arms) are applied in the vehicle's local frame before storing positions in ENU.

**Offset Application**:

These offsets are set via `GNSSReceiver`

configuration methods:

`setAntennaToChipOffset(double xOffset, double yOffset, double zOffset)`

`setChipToBaseOffset(double xOffset, double yOffset, double zOffset)`

Sources: sensors/gnss/gnssreceiver.cpp86-102 sensors/gnss/gnssreceiver.h74-76

PX4 flight controllers maintain their own EKF with a GPS global origin that may differ from WayWise's ENU reference.

| Variable | Frame | Purpose |
|---|---|---|
`mEnuReference` | ENU | WayWise's working coordinate system origin |
`mGpsGlobalOrigin` | NED | PX4's on-board EKF origin, used for precision landing |

**Why Both Exist**:

`mEnuReference`

is user-controlled and consistent across all WayWise components`mGpsGlobalOrigin`

is set by PX4 and cannot be changed during flight`mGpsGlobalOrigin`

**Usage Example - Precision Landing**:

Sources: communication/vehicleconnections/mavsdkvehicleconnection.h81-83 communication/vehicleconnections/mavsdkvehicleconnection.cpp617-653

All WayWise internal computations (autopilot, sensor fusion, state management) operate in ENU. Convert from external formats (LLH, NED) at system boundaries.

All components should share the same ENU reference point. Synchronize via:

`MapWidget::enuRefChanged`

signal`MavsdkVehicleConnection::pollCurrentENUreference()`

to query vehicle-side referenceThe ENU→LLH transformation assumes a flat Earth locally. Errors grow with distance from the reference point. Keep operations within ~10 km of the reference.

When defining interfaces that pass position data, clearly document the coordinate frame:

Sources: communication/vehicleconnections/vehicleconnection.h48 communication/vehicleconnections/mavsdkvehicleconnection.cpp538-546

| From | To | Function | Notes |
|---|---|---|---|
| LLH | ENU | `coordinateTransforms::llhToEnu(reference, position)` | Requires ENU reference point |
| ENU | LLH | `coordinateTransforms::enuToLlh(reference, position)` | Requires ENU reference point |
| NED | ENU | `coordinateTransforms::nedToENU(nedPos)` | Swaps axes, negates Z |
| ENU | NED | `coordinateTransforms::enuToNED(enuPos)` | Swaps axes, negates Z |
| NED yaw | ENU yaw | `coordinateTransforms::yawNEDtoENU(yawNED)` | Handles angle convention |
| ENU yaw | NED yaw | `coordinateTransforms::yawENUtoNED(yawENU)` | Handles angle convention |

Sources: communication/vehicleconnections/mavsdkvehicleconnection.cpp96 communication/vehicleconnections/mavsdkvehicleconnection.cpp112 communication/vehicleconnections/mavsdkvehicleconnection.cpp132 communication/vehicleconnections/mavsdkvehicleconnection.cpp139 communication/vehicleconnections/mavsdkvehicleconnection.cpp541 communication/vehicleconnections/mavsdkvehicleconnection.cpp562-563

Refresh this wiki
