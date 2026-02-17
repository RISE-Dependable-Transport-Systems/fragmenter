# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/7-route-planning-and-utilities

This page documents WayWise's route planning utilities, which provide the foundation for route creation, coordinate transformations, and geometric calculations. The system is organized into three main categories:

`coordinateTransforms`

namespace for converting between GPS (LLH), local planning (ENU), and MAVLink (NED) frames`PosPoint`

data structure and `PosType`

enumeration for multi-source position tracking`ZigZagRouteGenerator`

class for algorithmic coverage patterns and `RouteUtils`

functions for file I/ORoutes are represented as `QList<PosPoint>`

, where each `PosPoint`

contains position (x, y, height), speed, attributes, and metadata. These routes flow from creation (UI or algorithm) through upload (MAVLink) to execution (autopilot).

**Key Files:**

**Related Pages:**

`PurepursuitWaypointFollower`

`PlanUI`

`VehicleState`

position tracking architecture**Sources:** routeplanning/routeutils.h1-22 routeplanning/zigzagroutegenerator.h1-36 examples/RCCar_ISO22133_autopilot/CMakeLists.txt53-54 examples/RCCar_MAVLINK_autopilot/CMakeLists.txt52-53

WayWise routes are authored in GPS coordinates (latitude/longitude) but executed in local Cartesian coordinates. The `coordinateTransforms`

namespace provides conversion functions between three coordinate systems, while `VehicleState`

and `ObjectState`

maintain the ENU reference point used as the origin for all planning operations.

This section is documented in detail on page 7.1. Key concepts include:

`ObjectState::mEnuReference`

(llh_t), automatically initialized from first GNSS fix`coordinateTransforms::llhToEnu()`

, `coordinateTransforms::enuToLlh()`

, `coordinateTransforms::yawNEDtoENU()`

`coordinateTransforms::ENUToVehicleFrame()`

transforms global points to vehicle-relative coordinates**Title:** Three Coordinate Systems in WayWise

**Coordinate System Properties:**

`ObjectState::mEnuReference`

)**Sources:** vehicles/objectstate.h55-57 vehicles/objectstate.h87 core/coordinatetransforms.h

The ENU reference point is stored in `ObjectState::mEnuReference`

and serves as the origin for all local coordinates. When not explicitly set, it is automatically initialized to the first GNSS position received.

**Title:** ENU Reference Point Initialization and Storage

**Key Behaviors:**

`mEnuReferenceSet == false`

(see sensors/gnss/ubloxrover.cpp)`MapWidget::setEnuRef()`

(Ctrl+Shift+Click on map)`updatedEnuReference()`

signal for UI updates**Sources:** vehicles/objectstate.h55-57 vehicles/objectstate.h87-88 vehicles/objectstate.cpp60-70 userinterface/map/mapwidget.cpp272-278 userinterface/map/mapwidget.h67-68

**Title:** Coordinate Frame Usage Across System Components

**Common Transformation Patterns:**

`UbloxRover`

for position updates`MapWidget`

transforms**Sources:** sensors/gnss/ubloxrover.cpp355-401 routeplanning/routeutils.cpp7-79 vehicles/vehiclestate.cpp102-107 core/coordinatetransforms.h

`PosPoint`

is the core data structure for representing positions throughout WayWise. It stores position (x, y, height), orientation (yaw), velocity, time, accuracy, and user-defined attributes. The system tracks multiple position sources simultaneously using the `PosType`

enumeration.

This section is documented in detail on page 7.2. Key concepts include:

**Title:** PosPoint Data Structure and Multi-Source Tracking

**Key Methods:**

`getPosition(PosType type)`

: Retrieve position from specific source (O(1) array access)`setPosition(PosPoint& point)`

: Update position for point's type, emits `positionUpdated(PosType)`

signal`PosPoint::getXYZ()`

, `setXYZ(xyz_t)`

: 3D position access`PosPoint::updateWithOffsetAndYawRotation(xyz_t, double)`

: Apply coordinate transformation**Sources:** vehicles/objectstate.h59-62 vehicles/objectstate.h96 vehicles/objectstate.cpp16-26 vehicles/objectstate.cpp38-43 vehicles/objectstate.cpp55-58 core/pospoint.h

Different subsystems select position sources based on requirements. The `PurepursuitWaypointFollower`

uses `mPosTypeUsed`

to specify which source to use for control:

| Subsystem | Typical PosType | Configuration |
|---|---|---|
`PurepursuitWaypointFollower` | `PosType::fused` | Set via `mPosTypeUsed` member |
`UbloxRover` GNSS updates | `PosType::GNSS` | Hardcoded in receiver code |
| Odometry updates | `PosType::odom` | Updated by `updateOdomPositionAndYaw()` |
| Simulation | `PosType::simulated` | Used for testing without hardware |

The autopilot retrieves position via: `PosPoint currentPos = mVehicleState->getPosition(mPosTypeUsed);`


This allows dynamic source switching (e.g., fallback to odometry during GNSS outages) by changing `mPosTypeUsed`

.

**Sources:** vehicles/objectstate.h59-62 vehicles/objectstate.cpp55-58 vehicles/vehiclestate.h96

See page 7.2 for complete documentation of `PosPoint`

fields, methods, and multi-source tracking architecture.

The `coordinateTransforms`

namespace provides the mathematical foundation for route planning workflows:

**LLH to ENU Conversion**: Projects geodetic coordinates onto a local tangent plane using the ENU reference point as origin. The transformation accounts for Earth's curvature over short distances.

**NED to ENU Yaw Conversion**:

`yaw_enu = 90° - yaw_ned`

**Sources:** core/coordinatetransforms.h core/coordinatetransforms.cpp

See page 7.1 for detailed examples of coordinate transformation usage in GNSS processing, route import, and autopilot calculations.

WayWise provides two main utilities for route generation and management:

Static class providing geometric algorithms for coverage route generation. All methods are static utility functions.

**Title:** ZigZagRouteGenerator Function Categories

**Primary Use Cases:**

**Sources:** routeplanning/zigzagroutegenerator.h12-35 routeplanning/zigzagroutegenerator.cpp8-447

The `fillConvexPolygonWithZigZag()`

method generates boustrophedon (back-and-forth) coverage patterns:

**Title:** Six-Step Zigzag Generation Process

**Function Signature:**

```
static QList<PosPoint> fillConvexPolygonWithZigZag(
QList<PosPoint> bounds, // Polygon vertices (ENU)
double spacing, // Pass separation (m)
bool keepTurnsInBounds, // Constrain turns to polygon
double speed, // Straight segment speed (m/s)
double speedInTurns, // Turn segment speed (m/s)
int turnIntermediateSteps, // Points per U-turn
int visitEveryX, // Multi-pass pattern (0=single pass)
uint32_t setAttributesOnStraights, // Bitmask for straights
uint32_t setAttributesInTurns, // Bitmask for turns
double attributeDistanceAfterTurn, // Offset from turn end
double attributeDistanceBeforeTurn // Offset from turn start
);
```


**Sources:** routeplanning/zigzagroutegenerator.h24-25 routeplanning/zigzagroutegenerator.cpp167-392

`getBaselineDeterminingMinHeightOfConvexPolygon()`

minimizes the number of zigzag passes by choosing the polygon edge with the smallest maximum distance to opposite vertices.

**Title:** Baseline Selection Algorithm

**Rationale:** Choosing the edge with minimum "height" (maximum distance to opposite vertices) minimizes the number of parallel passes needed, optimizing coverage efficiency.

**Sources:** routeplanning/zigzagroutegenerator.h23 routeplanning/zigzagroutegenerator.cpp141-165

Raw zigzag routes have 180° corners infeasible for ground vehicles. The algorithm inserts `turnIntermediateSteps`

waypoints to create circular arcs:

**Turn Generation Parameters:**

`turnRadius = spacing / 2`

(or `visitEveryX * spacing / 2`

for multi-pass)`turnCenter`

computed perpendicular to sweep direction`turnIntermediateSteps + 2`

waypoints (includes start/end)`speedInTurns`

(typically lower than straight speed)`keepTurnsInBounds = true`

constrains arc to stay within polygon**Example:** With `spacing = 4m`

and `turnIntermediateSteps = 5`

, generates 7-point arc with 2m radius connecting passes.

**Sources:** routeplanning/zigzagroutegenerator.cpp246-362

**Attribute System:** Each `PosPoint`

has a 32-bit `attributes`

bitmask for control logic. The generator applies attributes to specific segments:

`setAttributesOnStraights`

: Applied to straight passes (with offset from turns)`setAttributesInTurns`

: Applied to turn waypoints`setAttributesOnStraights = 0x01`

to spray only on straights**Multi-Pass Coverage ( visitEveryX):** Visit every Nth line per pass, then return to cover skipped lines. Useful for rapid initial coverage.

**Framed Zigzag ( fillConvexPolygonWithFramedZigZag):**

`getShrinkedConvexPolygon(bounds, spacing)`

`fillConvexPolygonWithZigZag(frame, ...)`

**Use Case:** Ensures complete edge coverage before filling interior (critical for boundary precision).

**Sources:** routeplanning/zigzagroutegenerator.h26-27 routeplanning/zigzagroutegenerator.cpp366-415

Namespace providing helper functions for route file I/O and geometric calculations.

**Title:** RouteUtils Functions

**Key Functions:**

| Function | Purpose | Algorithm |
|---|---|---|
`readRouteFromFile()` | Import route from XML with ENU conversion | Parse XML → LLH → vehicle ENU |
`isPointWithin()` | Point-in-polygon test (geofencing) | Ray casting (O(n) where n = vertices) |

**XML Import Process:**

`<enuref>`

to get `importedEnuRef`

(LLH)`<point>`

elements to get ENU coordinates`importedENU → LLH (absolute) → vehicleENU`

**Sources:** routeplanning/routeutils.h19-21 routeplanning/routeutils.cpp7-107

The `isPointWithin()`

function is used for:

**Implementation:** Ray casting - count polygon edge crossings of horizontal ray from test point. Odd count = inside, even count = outside.

**Autopilot Integration:** `PurepursuitWaypointFollower`

calls `ZigZagRouteGenerator::isPointWithin(currentPos, region.boundary)`

to apply speed limit regions.

**Sources:** routeplanning/routeutils.cpp81-107

See page 7.3 for complete documentation of `ZigZagRouteGenerator`

algorithms and `RouteUtils`

functions.

Routes flow through multiple subsystems from creation to execution. This section illustrates the complete lifecycle.

**Title:** Route Planning and Execution Data Flow

**Sources:** userinterface/map/routeplannermodule.cpp communication/vehicleconnections/vehicleconnection.cpp autopilot/purepursuitwaypointfollower.cpp39-48 autopilot/purepursuitwaypointfollower.cpp118-148

The route planning utilities are deeply integrated with the `VehicleState`

class, which provides the ENU reference frame and position tracking for coordinate transformations.

`VehicleState`

provides convenience methods for transforming between ENU and vehicle-local frames:

** posInVehicleFrameToPosPointENU(xyz_t offset, PosType type)**:

`PosPoint`

with the transformed position** getCurvatureToPointInENU(QPointF point, PosType type)**:

**Sources:** vehicles/vehiclestate.h77-97 vehicles/vehiclestate.cpp92-133

Vehicles with trailers require special coordinate transformations to track both the truck and trailer positions independently.

The trailer's position is computed by:

**Sources:** vehicles/truckstate.cpp58-82 vehicles/truckstate.h30-36

`getPosition(PosType)`

is O(1) via direct array access`mPositionBySource[]`

`updateWithOffsetAndYawRotation()`

modifies `PosPoint`

directly, avoiding allocations**Sources:** vehicles/vehiclestate.cpp87-89 core/geometry.cpp autopilot/purepursuitwaypointfollower.cpp386-391

```
// GNSS receiver updates position
llh_t llh = {pvt.lat, pvt.lon, pvt.height};
xyz_t xyz = coordinateTransforms::llhToEnu(mVehicleState->getEnuRef(), llh);
PosPoint gnssPos = mVehicleState->getPosition(PosType::GNSS);
gnssPos.setXYZ(xyz);
gnssPos.setYaw(yaw_degENU);
mVehicleState->setPosition(gnssPos);
```


**Sources:** sensors/gnss/ubloxrover.cpp355-401

```
// Autopilot reads position for control
PosPoint currentPos = mVehicleState->getPosition(mPosTypeUsed);
QPointF positionXY = currentPos.getPoint();
double yaw = currentPos.getYaw();
```


**Sources:** autopilot/purepursuitwaypointfollower.cpp51-59 autopilot/purepursuitwaypointfollower.cpp383-384

```
// Transform antenna position to vehicle reference point
double yawRad = getPosition(type).getYaw() * M_PI / 180.0;
gnssPos.updateWithOffsetAndYawRotation(mChipToRearAxleOffset, yawRad);
```


**Sources:** sensors/gnss/ubloxrover.cpp382-393

```
// Check if vehicle is inside speed limit region
PosPoint currentPos = mVehicleState->getPosition(mPosTypeUsed);
for (const SpeedLimitRegion ®ion : mSpeedLimitRegions) {
if (ZigZagRouteGenerator::isPointWithin(currentPos, region.boundary)) {
cappedSpeed = std::min(cappedSpeed, region.maxSpeed);
}
}
```


Refresh this wiki
