# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/4.1-state-architecture-and-position-sources

This document describes the foundational state management architecture in WayWise, focusing on the `ObjectState`

and `VehicleState`

base classes. These classes provide the core infrastructure for tracking object position, velocity, and configuration across multiple position sources simultaneously.

Key topics covered:

`mPositionBySource`

array that maintains six concurrent position estimatesFor vehicle-specific implementations (car, truck, copter), see Ground Vehicle Models, Articulated Vehicles, and Multicopter State. For sensor fusion algorithms that produce the fused position, see Sensor Fusion Algorithm.

The `ObjectState`

class (vehicles/objectstate.h8-100) serves as the foundation for all moveable and immoveable objects in WayWise, including vehicles, cameras, and other tracked entities.

**Diagram: ObjectState and VehicleState class hierarchy**

Sources: vehicles/objectstate.h8-100 vehicles/vehiclestate.h8-133

| Property | Type | Purpose |
|---|---|---|
`mId` | `ObjectID_t` (int) | Unique identifier for the object |
`mName` | `QString` | Human-readable name (default: "Vehicle N") |
`mColor` | `Qt::GlobalColor` | Display color for visualization |
`mWaywiseObjectType` | `WAYWISE_OBJECT_TYPE` | Object type classification (CAR, TRUCK, TRAILER, QUADCOPTER, GENERIC) |
`mEnuReference` | `llh_t` | Origin point for local ENU coordinate system |
`mEnuReferenceSet` | `bool` | Flag indicating if ENU reference has been initialized |
`mPositionBySource` | `PosPoint[6]` | Array of positions from different sources |
`mSpeed` | `double` | Current speed in m/s |
`mVelocity` | `xyz_t` | Velocity vector in m/s |
`mAcceleration` | `xyz_t` | Acceleration vector in m/s² |

Sources: vehicles/objectstate.h79-96

The constructor (vehicles/objectstate.cpp10-26) initializes the `mPositionBySource`

array, setting the correct `PosType`

for each array element:

Sources: vehicles/objectstate.cpp10-26

The core innovation of `ObjectState`

is the `mPositionBySource`

array (vehicles/objectstate.h96), which maintains six concurrent position estimates from different sources. This architecture allows the system to:

The `PosType`

enum (defined in `core/pospoint.h`

) specifies the six position sources:

| Index | PosType | Description | Typical Use Case |
|---|---|---|---|
| 0 | `simulated` | Simulated/commanded position | Testing, simulation, ground station display |
| 1 | `fused` | Sensor-fused optimal estimate | Primary position for autopilot control |
| 2 | `odom` | Odometry-based dead reckoning | Wheel encoder integration, relative motion |
| 3 | `IMU` | IMU-based position estimate | High-rate orientation updates |
| 4 | `GNSS` | Raw GNSS receiver output | Absolute position reference |
| 5 | `UWB` | Ultra-wideband positioning | Indoor/GPS-denied environments |

Sources: vehicles/objectstate.h96 vehicles/objectstate.cpp16-24

**Diagram: Multi-source position tracking data flow**

Sources: vehicles/objectstate.h96 vehicles/objectstate.cpp38-43 vehicles/objectstate.cpp55-58

Position updates occur through the `setPosition()`

method (vehicles/objectstate.cpp38-43):

This design:

Position retrieval uses `getPosition(PosType type)`

(vehicles/objectstate.cpp55-58):

Sources: vehicles/objectstate.cpp38-43 vehicles/objectstate.cpp55-58

WayWise uses a local **East-North-Up (ENU)** coordinate system for all position calculations. The ENU reference point is stored as a geographic coordinate (`llh_t`

structure with latitude, longitude, height).

| Method | Purpose |
|---|---|
`getEnuRef()` | Returns the current ENU origin point |
`setEnuRef(llh_t enuRef)` | Sets the ENU origin and emits `updatedEnuReference` signal |
`isEnuReferenceSet()` | Checks if ENU reference has been initialized |

Default ENU reference (vehicles/objectstate.h87):

The ENU reference point defines:

When the ENU reference changes, all position sources remain in local ENU coordinates relative to the new origin. The `updatedEnuReference`

signal (vehicles/objectstate.cpp60-65) notifies subscribers to handle the reference change.

Sources: vehicles/objectstate.h55-57 vehicles/objectstate.h87 vehicles/objectstate.cpp60-65

`VehicleState`

(vehicles/vehiclestate.h25-131) extends `ObjectState`

with vehicle-specific properties and behaviors.

These properties define the physical characteristics and limits of the vehicle:

| Property | Type | Default | Description |
|---|---|---|---|
`mLength` | `double` | 0.8 m | Vehicle length |
`mWidth` | `double` | 0.335 m | Vehicle width |
`mMinAcceleration` | `double` | -5.0 m/s² | Maximum braking deceleration |
`mMaxAcceleration` | `double` | 3.0 m/s² | Maximum forward acceleration |
`mRearAxleToCenterOffset` | `xyz_t` | - | Offset from rear axle to vehicle center |
`mRearAxleToRearEndOffset` | `xyz_t` | {-0.1333, 0, 0} | Offset from rear axle to vehicle rear |
`mRearAxleToHitchOffset` | `xyz_t` | - | Offset from rear axle to trailer hitch |

The rear axle is used as the vehicle's reference point for control calculations (see Ground Vehicle Models).

Sources: vehicles/vehiclestate.h107-115

These properties track the current vehicle state:

| Property | Type | Description |
|---|---|---|
`mSteering` | `double` | Normalized steering [-1.0, 1.0] |
`mFlightMode` | `FlightMode` | Current flight/drive mode |
`mIsArmed` | `bool` | Vehicle armed status |
`mHomePosition` | `PosPoint` | Home/takeoff position |
`mAutopilotRadius` | `double` | Target radius for autopilot |
`mAutopilotTargetPoint` | `QPointF` | Current autopilot target |
`mEndGoalAlignmentType` | `AutopilotEndGoalAlignmentType` | End goal alignment strategy |
`mGyroscopeXYZ` | `std::array<float, 3>` | Gyroscope readings [deg/s] |
`mAccelerometerXYZ` | `std::array<float, 3>` | Accelerometer readings [g] |

Sources: vehicles/vehiclestate.h118-130

The `FlightMode`

enum (vehicles/vehiclestate.h30-46) mirrors the MAVSDK FlightMode enumeration:

This allows consistent flight mode tracking across MAVLink communication and local state management.

Sources: vehicles/vehiclestate.h30-46 vehicles/vehiclestate.h73-81

`VehicleState`

defines two pure virtual methods that child classes must implement:

** updateOdomPositionAndYaw()**: Updates the odometry-based position using the kinematic model specific to the vehicle type (bicycle model for cars, differential drive for robots, etc.). This integrates wheel encoder data to maintain the

`PosType::odom`

position source.** steeringCurvatureToSteering()**: Converts a desired path curvature (from pure pursuit or other path-following algorithms) to a vehicle-specific steering command. Implementation depends on vehicle geometry (wheelbase, steering angle limits).

Sources: vehicles/vehiclestate.h96-97

`VehicleState`

provides methods for transforming positions between coordinate frames.

**Diagram: Coordinate frame transformation from vehicle frame to ENU**

The `posInVehicleFrameToPosPointENU()`

method (vehicles/vehiclestate.cpp66-71) performs this transformation:

This is used to calculate positions of vehicle points other than the rear axle (e.g., front axle, hitch point, trailer attachment) in the global ENU coordinate system.

Sources: vehicles/vehiclestate.cpp66-71 vehicles/vehiclestate.h71-72

Path-following algorithms (particularly pure pursuit) require calculating the curvature to a target point. `VehicleState`

provides two methods:

`getCurvatureToPointInVehicleFrame()`

(vehicles/vehiclestate.cpp93-100) implements the pure pursuit curvature formula:

The formula κ = 2y/(x²+y²) comes from the pure pursuit algorithm, where (x, y) is the lookahead point in vehicle coordinates.

`getCurvatureToPointInENU()`

(vehicles/vehiclestate.cpp102-107) transforms an ENU point to vehicle frame, then calculates curvature:

This allows autopilot systems to calculate steering commands directly from global waypoint coordinates.

Sources: vehicles/vehiclestate.cpp93-107 vehicles/vehiclestate.h87-88

`VehicleState`

supports **composition of multiple vehicles** through the trailing vehicle pattern, enabling multi-body dynamics for truck-trailer combinations.

**Diagram: Trailing vehicle composition pattern enabling multi-body vehicles**

| Method | Purpose |
|---|---|
`getTrailingVehicle()` | Returns shared pointer to trailing vehicle (or null) |
`setTrailingVehicle(QSharedPointer<VehicleState> trailer)` | Attaches a trailing vehicle |
`hasTrailingVehicle()` | Returns true if a trailing vehicle is attached |

Implementation (vehicles/vehiclestate.cpp109-122):

This pattern enables:

For implementation details on trailer dynamics, see Articulated Vehicles.

Sources: vehicles/vehiclestate.h90-94 vehicles/vehiclestate.h127 vehicles/vehiclestate.cpp109-122

The state architecture provides:

`mPositionBySource[6]`

array, enabling simultaneous tracking of simulated, fused, odometry, IMU, GNSS, and UWB positions`ObjectState`

(generic) to `VehicleState`

(vehicle-specific) to specialized types (car, truck, copter)This architecture supports:

Sources: vehicles/objectstate.h8-100 vehicles/objectstate.cpp1-71 vehicles/vehiclestate.h8-133 vehicles/vehiclestate.cpp1-123

Refresh this wiki
