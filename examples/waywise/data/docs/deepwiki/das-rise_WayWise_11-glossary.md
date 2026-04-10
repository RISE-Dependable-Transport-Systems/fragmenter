# Source: https://deepwiki.com/das-rise/WayWise/11-glossary

This page provides technical definitions and implementation details for domain-specific terms and core abstractions used within the WayWise codebase.

The fundamental data structure for representing a spatial point with kinematic metadata. It encapsulates 3D coordinates, orientation, speed, and timing information.

`PosPoint`

uses an `xyz_t`

struct for ENU coordinates and provides helper methods for distance calculation and offset application.`X`

, `Y`

, `Z`

: Coordinates in the Local Tangent Plane (ENU).`Yaw`

: Orientation in degrees.`Speed`

: Target or current velocity in m/s.`Radius`

: Acceptance radius for waypoint reaching or pure pursuit look-ahead.An enumeration used to distinguish between different sources of positioning data. This allows the system to maintain multiple estimates of the vehicle's state simultaneously (e.g., raw GNSS vs. fused odometry).

`fused`

, `gnss`

, `odom`

, `uwb`

, `simulated`

, `depthai`

.`ObjectState`

maintains an array of `PosPoint`

indexed by `PosType`

vehicles/objectstate.h47-48WayWise primarily operates in the **ENU** (East-North-Up) Cartesian frame for internal logic and UI rendering, while **NED** (North-East-Down) is used for MAVLink telemetry and aeronautical conventions.

`coordinateTransforms`

namespace.The vehicle state system uses a hierarchical inheritance model to represent different kinematics and physical properties.

The base class for any tracked object. It manages the `EnuRef`

(the WGS84 origin for the local Cartesian coordinate system) and the `mPositionBySource`

array.

An abstract specialization of `ObjectState`

adding vehicle-specific dynamics like steering, arming status, and flight modes. It introduces the `getCurvatureToPointInVehicleFrame`

method used by autopilots.

`CarState`

to support articulated vehicles with trailers. It includes logic for `getCurvatureWithTrailer`

to handle reversing and forward-moving trailer kinematics.The following diagram maps the relationship between high-level concepts and the C++ classes.

**Diagram: Vehicle State Class Hierarchy**

Sources: vehicles/objectstate.h23-30 vehicles/vehiclestate.h25-48 vehicles/carstate.h13-20 vehicles/truckstate.h13-17

A path-tracking algorithm that calculates the curvature required for a vehicle to move from its current position to a "look-ahead" point on the path.

`PurepursuitWaypointFollower`

calculates the steering curvature based on the lateral offset of a goal point relative to the vehicle's heading.`PP_RADIUS`

. It can be adaptive based on speed using `PP_ARC`

.A dynamic navigation mode where the vehicle follows a moving target (e.g., another vehicle or a person) rather than a static route.

`FollowPoint`

class. It uses a heartbeat watchdog (`mFollowPointHeartbeatTimer`

) to ensure the target is still active.`followPointMaximumDistance`

to prevent the vehicle from chasing a lost target.The state machine governing the execution of a route.

`NONE`

, `FOLLOW_ROUTE_INIT`

, `FOLLOW_ROUTE_FOLLOWING`

, `FOLLOW_ROUTE_APPROACHING_END_GOAL`

, `FOLLOW_ROUTE_FINISHED`

.**Diagram: Communication Flow (MAVSDK)**

Sources: communication/mavsdkvehicleserver.cpp48-78 communication/vehicleconnections/mavsdkvehicleconnection.cpp108-115 communication/vehicleconnections/mavsdkvehicleconnection.cpp41-42

A centralized registry for configuration values (`int`

, `float`

, `string`

) that can be synced over the network via MAVLink `PARAM`

protocols.

`provideParametersToParameterServer()`

to register their internal variables (e.g., `PP_RADIUS`

).Radio Technical Commission for Maritime Services. Binary data format used to provide GNSS corrections to a receiver (Rover) to achieve RTK (Real-Time Kinematic) precision (centimeter-level).

`UbloxRover::writeRtcmToUblox`

forwards these bytes to the ZED-F9P chip.The 3D offset between the GNSS antenna and the vehicle's reference point (usually the center of the rear axle).

U-blox specific protocol for combining IMU and Wheel Tick data with GNSS.

| Abbreviation | Full Term | Context |
|---|---|---|
LLH | Latitude, Longitude, Height | WGS84 Global coordinates. |
ENU | East, North, Up | Local Cartesian frame used for planning. |
NED | North, East, Down | Standard aeronautical coordinate frame. |
VESC | Vedder Electronic Speed Controller | Hardware interface for motor control. |
PDO/SDO | Process/Service Data Object | CANopen communication primitives. |
RTK | Real-Time Kinematic | High-precision GNSS positioning. |
STM | State Machine | Logic flow for autopilots and followers. |

Sources: core/coordinatetransforms.h15-20 autopilot/purepursuitwaypointfollower.h21 sensors/gnss/ubloxrover.cpp114-132

Refresh this wiki

This wiki was recently refreshed. Please wait 6 days to refresh again.