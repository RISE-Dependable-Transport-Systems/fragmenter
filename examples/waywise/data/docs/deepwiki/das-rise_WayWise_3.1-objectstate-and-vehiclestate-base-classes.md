# Source: https://deepwiki.com/das-rise/WayWise/3.1-objectstate-and-vehiclestate-base-classes

The `ObjectState`

and `VehicleState`

classes form the foundational data structures for representing any entity within the WayWise ecosystem. `ObjectState`

serves as the generic base for any movable or immovable object, handling multi-source positioning and global reference frames. `VehicleState`

extends this to include kinematic properties, autopilot targets, and control states specific to mobile platforms.

`ObjectState`

is the root class for all stateful entities in the codebase vehicles/objectstate.h31 It manages static properties like unique identifiers, names, and display colors, alongside dynamic properties like velocity, acceleration, and a sophisticated multi-source position array.

A key feature of `ObjectState`

is the `mPositionBySource`

array vehicles/objectstate.h96 This allows the system to simultaneously track the position of an object from multiple independent sources (e.g., GNSS, IMU, Odometry, or Fused results).

Source Type (`PosType` ) | Description |
|---|---|
`simulated` | Predicted position based on internal models. |
`fused` | Result of sensor fusion algorithms. |
`odom` | Relative movement calculated from wheel encoders. |
`GNSS` | Absolute global position from satellite receivers. |
`IMU` | Orientation and acceleration-based dead reckoning. |
`UWB` | Position relative to Ultra-Wideband anchors. |

The constructor initializes this array by mapping each `PosType`

to its corresponding index vehicles/objectstate.cpp16-25 When `setPosition()`

is called, it updates the specific slot in the array and emits the `positionUpdated(PosType type)`

signal vehicles/objectstate.cpp38-43

To facilitate local navigation, `ObjectState`

maintains an ENU (East-North-Up) reference point (`mEnuReference`

) vehicles/objectstate.h87 This LLH (Latitude, Longitude, Height) coordinate serves as the origin for local Cartesian transforms. When a new reference is set via `setEnuRef()`

, the class emits `updatedEnuReference`

to notify subscribers (such as UI maps or autopilot controllers) vehicles/objectstate.cpp60-65

**Sources:** vehicles/objectstate.h1-101 vehicles/objectstate.cpp1-71

`VehicleState`

inherits from `ObjectState`

and adds vehicle-specific attributes required for navigation and control vehicles/vehiclestate.h25 It introduces physical dimensions, steering limits, and high-level autopilot goals.

`VehicleState`

defines several physical parameters used for coordinate transformations and rendering:

`mLength`

and `mWidth`

vehicles/vehiclestate.h107-108`mRearAxleToCenterOffset`

, `mRearAxleToRearEndOffset`

, and `mRearAxleToHitchOffset`

vehicles/vehiclestate.h113-115 These offsets are critical for calculating the precise location of sensors or hitch points relative to the vehicle's control frame (usually the rear axle).The class implements a `FlightMode`

enum that mirrors MAVSDK conventions, supporting modes such as `Mission`

, `Hold`

, `Offboard`

, and `FollowMe`

vehicles/vehiclestate.h30-46 It also stores autopilot-specific targets:

`mAutopilotTargetPoint`

`mAutopilotRadius`

`AutopilotEndGoalAlignmentType`

`REAR_AXLE`

, `CENTER`

, or `FRONT_REAR_END`

with the final target vehicles/vehiclestate.h23`VehicleState`

provides helper functions to calculate the required curvature to reach a specific point.

`getCurvatureToPointInVehicleFrame()`

: Implements the pure pursuit law, where $curvature = \frac{2 \cdot y}{L^2}$ (where $y$ is the lateral offset and $L$ is the look-ahead distance) vehicles/vehiclestate.cpp93-100`getCurvatureToPointInENU()`

: Automatically transforms an ENU coordinate into the vehicle's local frame before calculating curvature vehicles/vehiclestate.cpp102-107**Sources:** vehicles/vehiclestate.h1-134 vehicles/vehiclestate.cpp1-123

The following diagrams illustrate how the `ObjectState`

and `VehicleState`

entities bridge the gap between high-level navigation concepts and low-level code implementations.

This diagram shows how generic object properties flow into specialized vehicle states and how they link to external components like trailers.

**Sources:** vehicles/objectstate.h25-31 vehicles/vehiclestate.h25 vehicles/vehiclestate.h127

This diagram traces the flow from receiving a new position to calculating a steering curvature for the autopilot.

**Sources:** vehicles/objectstate.cpp38-43 vehicles/vehiclestate.cpp102-107 vehicles/vehiclestate.cpp93-100

| Class | Function | Purpose |
|---|---|---|
`ObjectState` | `setPosition(PosPoint &point)` | Updates the specific `PosType` in the source array and signals listeners vehicles/objectstate.cpp38-43 |
`ObjectState` | `setEnuRef(llh_t enuRef)` | Sets the global origin for local coordinate transforms vehicles/objectstate.cpp60-65 |
`VehicleState` | `posInVehicleFrameToPosPointENU()` | Converts a local offset (e.g., sensor mount) to a global ENU coordinate based on current heading vehicles/vehiclestate.cpp66-71 |
`VehicleState` | `setSteering(double steering)` | Sets the steering value, clamped between -1.0 and 1.0 vehicles/vehiclestate.cpp38-44 |
`VehicleState` | `getCurvatureToPointInENU()` | High-level helper for pure-pursuit controllers to find the arc to a target vehicles/vehiclestate.cpp102-107 |
`VehicleState` | `setTrailingVehicle()` | Establishes a link to another `VehicleState` representing a trailer vehicles/vehiclestate.cpp114-117 |

**Sources:** vehicles/objectstate.cpp1-71 vehicles/vehiclestate.cpp1-123

Refresh this wiki

This wiki was recently refreshed. Please wait 7 days to refresh again.