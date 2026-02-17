# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/7.2-position-types-and-pospoint-structure

This document describes the `PosType`

enumeration and `PosPoint`

data structure, which are fundamental primitives for representing vehicle positions from multiple sensor sources in WayWise. These types enable the system to maintain and select from different position estimates (GNSS, odometry, sensor fusion, etc.) depending on availability and application requirements.

For information about coordinate system transformations (LLH, NED, ENU), see Coordinate Systems. For how positions are stored and managed within vehicle objects, see Vehicle State Architecture.

WayWise operates in environments where vehicles have access to multiple positioning sources with different characteristics. The system uses:

`PosType`

`PosPoint`

This design allows subsystems (autopilots, telemetry publishers, visualization) to select the most appropriate position source for their specific needs while maintaining a consistent interface.

**Sources:** vehicles/vehiclestate.h1-142 vehicles/vehiclestate.cpp1-149 autopilot/purepursuitwaypointfollower.h98

The `PosType`

enumeration defines the available position sources. Each vehicle maintains separate position estimates for each type, allowing dynamic selection based on sensor availability and requirements.

| PosType Value | Description | Typical Accuracy | Use Cases |
|---|---|---|---|
`simulated` | Virtual position for simulation and testing | Perfect (ground truth) | Software-in-the-loop testing, visualization |
`fused` | Position from external sensor fusion (e.g., u-blox ZED-F9R ESF) | cm-level (with RTK) | Primary position for autopilot when ESF is available |
`odom` | Dead-reckoning position from wheel encoders and steering | Drifts over time | Short-term position updates, backup when GNSS unavailable |
`IMU` | Position integrated from IMU measurements | Drifts quickly | High-rate updates between GNSS fixes |
`GNSS` | Raw GNSS receiver position without fusion | dm to cm-level | Primary position when ESF unavailable, telemetry |
`UWB` | Ultra-wideband ranging-based position | cm-level (line of sight) | Indoor positioning, GNSS-denied environments |

The enumeration uses a sentinel value `_LAST_`

to determine array sizing for position storage.

**Sources:** vehicles/vehiclestate.cpp13-23 vehicles/vehiclestate.h125

`PosPoint`

encapsulates a position estimate with its associated metadata. While the complete implementation is in `core/pospoint.h`

(not provided in the file list), its usage throughout the codebase reveals its interface and purpose.

**Position Coordinates:**

`x`

, `y`

: Position in ENU (East-North-Up) coordinates [meters]`height`

: Altitude above reference [meters]`yaw`

: Heading angle [degrees, 0° = East, 90° = North]**Motion State:**

`speed`

: Vehicle speed at this position [m/s], can be negative for reverse motion`attributes`

: Key-value map for application-specific data (e.g., trailer angle, gear state)**Metadata:**

`type`

: The `PosType`

identifying the source of this position`accuracy`

: Estimated position uncertainty [meters]**Key Methods:**

`getPoint()`

: Returns 2D position as `QPointF`

for XY operations`getXYZ()`

: Returns 3D position as `xyz_t`

structure`getDistanceTo(other)`

: Computes Euclidean distance to another `PosPoint`

`updateWithOffsetAndYawRotation(offset, yaw)`

: Applies coordinate frame transformation**Sources:** autopilot/purepursuitwaypointfollower.cpp49-297 vehicles/vehiclestate.cpp92-96

`VehicleState`

maintains separate `PosPoint`

instances for each `PosType`

, allowing concurrent position estimates from different sources. The storage uses an array indexed by the enumeration values.

The storage array is initialized in the `VehicleState`

constructor, setting each slot's `PosType`

:

vehicles/vehiclestate.cpp13-23

Access methods allow reading and writing positions by type:

**Write:** `setPosition(PosPoint& point)`

- stores the point in the slot corresponding to `point.getType()`


vehicles/vehiclestate.cpp27-32

**Read:** `getPosition(PosType type)`

- retrieves the position from the specified type's slot

vehicles/vehiclestate.cpp87-90

The default `getPosition()`

without arguments returns `PosType::simulated`

.

**Sources:** vehicles/vehiclestate.h71-125 vehicles/vehiclestate.cpp13-90

Autopilot implementations select which `PosType`

to use for path planning and control. This selection affects both accuracy and failure modes of autonomous navigation.

The `PurepursuitWaypointFollower`

stores a selected position type and uses it consistently throughout route execution:

**Default Selection:** The pure pursuit follower defaults to `PosType::fused`

, which prioritizes External Sensor Fusion (ESF) output when available:

autopilot/purepursuitwaypointfollower.h98

**Constructor Parameter:** When operating via `VehicleConnection`

(remote control mode), the position type is specified at construction:

autopilot/purepursuitwaypointfollower.cpp19-25

**Consistent Usage:** The selected type is used throughout the control loop:

**Sources:** autopilot/purepursuitwaypointfollower.h98 autopilot/purepursuitwaypointfollower.cpp19-395

`PosPoint`

objects support coordinate frame transformations, enabling conversion between vehicle-local and global reference frames. This is essential for control algorithms that compute steering commands in the vehicle frame.

`VehicleState::posInVehicleFrameToPosPointENU()`

converts an offset in the vehicle frame to a `PosPoint`

in ENU coordinates:

vehicles/vehiclestate.cpp92-97

This method:

`PosType`

`PosPoint`

in ENU coordinates**Usage Example:** Computing trailer position when backing:

autopilot/purepursuitwaypointfollower.cpp494-505

The inverse transformation (ENU to vehicle frame) is used by `getCurvatureToPointInENU()`

to compute steering commands:

vehicles/vehiclestate.cpp128-133

This method converts a target point from ENU to the vehicle's local frame, then computes the steering curvature using the pure pursuit algorithm.

**Sources:** vehicles/vehiclestate.cpp92-133 autopilot/purepursuitwaypointfollower.cpp494-505

`PosPoint`

objects in route waypoint lists carry speed information that is interpolated for intermediate target points. The `PurepursuitWaypointFollower`

implements linear speed interpolation:

autopilot/purepursuitwaypointfollower.cpp444-452

This interpolation:

`PosPoint`

The interpolated speed is used in control outputs: autopilot/purepursuitwaypointfollower.cpp267-282

**Sources:** autopilot/purepursuitwaypointfollower.cpp267-452

The `attributes`

field in `PosPoint`

is a key-value map (`QMap<QString, QVariant>`

) that carries application-specific metadata along with positions. This extensible design allows different vehicle types to attach relevant information without modifying the core `PosPoint`

structure.

Attributes are preserved through waypoint sequences:

autopilot/purepursuitwaypointfollower.cpp297

When computing intermediate goals between waypoints, the autopilot copies attributes from the closest waypoint, ensuring that waypoint-specific behaviors (e.g., "stop at this point", "change gear") are applied correctly.

Control commands receive these attributes: autopilot/purepursuitwaypointfollower.cpp381

**Potential Attribute Examples:**

**Sources:** autopilot/purepursuitwaypointfollower.cpp297-381

For vehicles with trailers, position calculations must account for articulation. The autopilot selects different reference positions based on direction of travel.

**Implementation:**

autopilot/purepursuitwaypointfollower.cpp46-55

**Rationale:** When backing with a trailer, the trailer's position is the leading edge and should be used for path following calculations. When moving forward, the vehicle's position is used. Both positions are stored as separate `PosPoint`

instances updated by the vehicle's state management.

**Sources:** autopilot/purepursuitwaypointfollower.cpp46-55

The `PosType`

and `PosPoint`

system provides:

This architecture enables robust autonomous navigation by allowing fallback between position sources (e.g., GNSS → odometry during signal loss) while maintaining clear semantics about which sensor is in use.

Refresh this wiki
