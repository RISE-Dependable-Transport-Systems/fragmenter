# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/4.3-articulated-vehicles-(truck-and-trailer)

This page documents the implementation of articulated vehicle dynamics in WayWise, specifically the `TruckState`

and `TrailerState`

classes that model multi-body ground vehicles with trailer attachments. These classes extend the Ackermann steering model to handle truck-trailer combinations with realistic kinematic behavior, trailer angle tracking, and trailer-aware path following control.

For single-body Ackermann vehicles without trailers, see Ground Vehicle Models (CarState). For general vehicle state management and position tracking, see State Architecture & Position Sources.

The articulated vehicle system uses composition to model the truck-trailer relationship, where a `TruckState`

instance maintains a reference to an optional `TrailerState`

instance.

**Sources:** vehicles/truckstate.h1-60 vehicles/trailerstate.h1-55 vehicles/carstate.h1-69

`TruckState`

extends `CarState`

to add trailer-specific functionality. It maintains trailer angle information, separate pure pursuit gains for forward and reverse motion, and overrides key methods to account for trailer dynamics.

| Member Variable | Type | Purpose |
|---|---|---|
`mPurePursuitForwardGain` | `double` | Gain applied to trailer angle error when moving forward (default: 1.0) |
`mPurePursuitReverseGain` | `double` | Gain applied to trailer angle error when reversing (default: -1.0) |
`mTrailerAngle_deg` | `double` | Current angle between truck and trailer in degrees |
`mSimulateTrailer` | `bool` | If true, trailer angle is estimated from kinematics; if false, external measurements are used |

**Sources:** vehicles/truckstate.h48-53

`TrailerState`

extends `VehicleState`

directly (not through `CarState`

) because trailers are passive vehicles controlled by the towing vehicle. The trailer maintains its own position, orientation, and geometric properties.

| Member Variable | Type | Purpose |
|---|---|---|
`mWheelBase` | `double` | Distance from trailer hitch to rear axle in meters |
`mAngle` | `double` | Current angle for standalone visualization |

**Sources:** vehicles/trailerstate.h44-47

The truck-trailer relationship is established through the `VehicleState::mTrailingVehicle`

shared pointer. `TruckState`

provides specialized accessors that downcast this pointer to `TrailerState`

.

The truck-trailer attachment is configured by calling:

**Sources:** vehicles/truckstate.cpp116-119 vehicles/truckstate.h30-31

| Reference Point | Vehicle | Description |
|---|---|---|
| Rear Axle | Truck | Primary position reference (0, 0) in vehicle frame |
| Hitch | Truck | Attachment point at rear of truck; offset from rear axle by `getRearAxleToHitchOffset()` |
| Hitch | Trailer | Attachment point at front of trailer; offset from trailer rear axle by `getRearAxleToHitchOffset()` |
| Rear Axle | Trailer | Primary position reference for trailer |

The hitch-to-rear-axle offset for the truck is automatically set to 10% of truck length when `setLength()`

is called:

**Sources:** vehicles/truckstate.cpp20-24

The trailer position is updated whenever the truck moves or its position changes. The algorithm maintains geometric consistency between the truck's hitch position and the trailer's hitch position.

**Sources:** vehicles/truckstate.cpp34-38 vehicles/truckstate.cpp58-82

The `updateTrailingVehicleOdomPositionAndYaw()`

method implements the following procedure:

**Calculate Truck Hitch Position** - Transform hitch offset from vehicle frame to ENU coordinates using the truck's current position and yaw:

**Get Current Trailer State**:

**Update Trailer Yaw** - Two modes:

**Simulation Mode** (`mSimulateTrailer == true`

and `usePosType == odom`

):

`setTrailerAngle((currYaw_rad - trailerYaw_rad) * 180.0 / M_PI)`

**External Measurement Mode**:

`mTrailerAngle_deg`

`trailerYaw_rad = currYaw_rad - getTrailerAngleRadians()`

**Set Trailer Hitch Position** - Place trailer hitch at truck hitch location:

**Calculate Trailer Rear Axle Position** - Offset from hitch to rear axle:

**Update Trailer State**:

**Sources:** vehicles/truckstate.cpp58-82

When `setPosition()`

is called on a `TruckState`

with a trailer, it triggers a zero-distance update to ensure the trailer position remains consistent:

**Sources:** vehicles/truckstate.cpp40-46

When a truck has a trailer attached, path following requires different steering control than a single-body vehicle. The `getCurvatureToPointInVehicleFrame()`

method is overridden to account for trailer dynamics.

**Sources:** vehicles/truckstate.cpp26-32 vehicles/truckstate.cpp84-107

When moving forward (`speed > 0`

), the algorithm targets the desired point directly and calculates the trailer angle needed to reach it:

Calculate angle error to target point:

Calculate desired trailer angle using kinematic relationship:

Use forward gain for error correction:

**Sources:** vehicles/truckstate.cpp92-95

When reversing (`speed ≤ 0`

), the trailer leads the motion. The algorithm considers the trailer's position and orientation:

Calculate trailer position in vehicle frame:

Calculate angle error from trailer to target, accounting for trailer orientation:

Calculate desired trailer angle using autopilot radius:

Use reverse gain (typically negative):

**Sources:** vehicles/truckstate.cpp97-103

Both forward and reverse modes use the same final curvature computation:

The formula combines:

`gain * (current - desired)`

`sin(angle) / wheelbase`

`1 / cos(angle)`

**Sources:** vehicles/truckstate.cpp105-106

Both `TruckState`

and `TrailerState`

register their parameters with the `ParameterServer`

for runtime configuration via MAVLink or UI.

`TruckState`

inherits all parameters from `CarState`

and adds truck-specific parameters:

| Parameter Name | Type | Description | Getter | Setter |
|---|---|---|---|---|
`VEH_RA2HO_X` | float | Rear axle to hitch offset (X component) | `getRearAxleToHitchOffset().x` | `setRearAxleToHitchOffset(double)` |

Additional parameters are inherited from `CarState`

: `VEH_LENGTH`

, `VEH_WIDTH`

, `VEH_WHLBASE`

, `VEH_RA2CO_X`

, `VEH_RA2REO_X`

, `PP_EGA_TYPE`

.

**Sources:** vehicles/truckstate.cpp126-139

| Parameter Name | Type | Description | Getter | Setter |
|---|---|---|---|---|
`TRLR_COMP_ID` | int | MAVLink component ID for trailer | `getId()` | `setId(int, false)` |
`TRLR_LENGTH` | float | Total trailer length in meters | `getLength()` | `setLength(double)` |
`TRLR_WIDTH` | float | Trailer width in meters | `getWidth()` | `setWidth(double)` |
`TRLR_WHLBASE` | float | Trailer wheelbase in meters | `getWheelBase()` | `setWheelBase(double)` |
`TRLR_RA2CO_X` | float | Rear axle to center offset (X) | `getRearAxleToCenterOffset().x` | `setRearAxleToCenterOffset(double)` |
`TRLR_RA2REO_X` | float | Rear axle to rear end offset (X) | `getRearAxleToRearEndOffset().x` | `setRearAxleToRearEndOffset(double)` |
`TRLR_RA2HO_X` | float | Rear axle to hitch offset (X) | `getRearAxleToHitchOffset().x` | `setRearAxleToHitchOffset(double)` |

Default trailer dimensions (from Griffin vehicle):

**Sources:** vehicles/trailerstate.cpp29-52 vehicles/trailerstate.cpp10-19

When a truck has a trailing vehicle attached, calling `provideParametersToParameterServer()`

on the truck recursively registers the trailer's parameters:

This enables multi-trailer configurations where each trailer's parameters are independently configurable.

**Sources:** vehicles/truckstate.cpp136-138

Both `TruckState`

and `TrailerState`

implement custom drawing methods for map display.

The `TruckState::draw()`

method extends `CarState::draw()`

to add:

`TrailerState::drawTrailer()`

if trailer attachedKey visualization elements:

**Sources:** vehicles/truckstate.cpp142-305

When displaying the turning radius and alignment point, the system selects the appropriate reference vehicle:

When reversing with a trailer, the trailer becomes the reference vehicle because it leads the motion.

**Sources:** vehicles/truckstate.cpp224-227

`TrailerState`

provides two drawing methods:

`drawTrailer()`

`draw()`

The `drawTrailer()`

method renders:

**Sources:** vehicles/trailerstate.cpp64-101 vehicles/trailerstate.cpp103-129

All drawing uses millimeter coordinates (scaled by 1000 from meters). The painter transform stack manages rotation and translation:

**Sources:** vehicles/truckstate.cpp159-189 vehicles/trailerstate.cpp79-81

The trailer-aware curvature calculation integrates seamlessly with the Pure Pursuit Waypoint Follower (see Pure Pursuit Waypoint Follower). The autopilot calls `getCurvatureToPointInVehicleFrame()`

without needing to know whether the vehicle has a trailer attached - polymorphism handles the dispatch to the correct implementation.

The separate forward and reverse gains (`mPurePursuitForwardGain`

and `mPurePursuitReverseGain`

) allow tuning of the control response for each direction independently. Typical values are:

**Sources:** vehicles/truckstate.h49-50 vehicles/truckstate.h24-28

Refresh this wiki
