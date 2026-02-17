# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/3.6-speed-limit-regions

This document describes the geofenced speed control system in WayWise, which allows defining polygonal regions with maximum speed limits. The system loads speed limit regions from GeoJSON files, converts geographic coordinates to the local ENU coordinate system, and dynamically enforces speed limits during route following by capping the desired speed when the vehicle is inside a region.

This feature is specifically integrated with the Pure Pursuit waypoint follower. For information about the Pure Pursuit algorithm itself, see Pure Pursuit Waypoint Follower. For coordinate system details, see Coordinate Systems & Transformations.

Speed limit regions provide dynamic speed control based on the vehicle's geographic position. The system operates on 2D polygons defined in WGS-84 coordinates (latitude/longitude), which are transformed to the local ENU coordinate system for efficient point-in-polygon testing during runtime.

**Sources:** autopilot/purepursuitwaypointfollower.cpp380-411 autopilot/purepursuitwaypointfollower.cpp570-672 autopilot/purepursuitwaypointfollower.h37-40

The `SpeedLimitRegion`

struct represents a single speed-controlled polygonal area.

| Field | Type | Description |
|---|---|---|
`boundary` | `QList<PosPoint>` | Ordered list of polygon vertices in ENU coordinates. If first point ≠ last point, the polygon is automatically closed. |
`maxSpeed` | `double` | Maximum allowed speed in meters per second within this region. |

**Key Characteristics:**

**Sources:** autopilot/purepursuitwaypointfollower.h37-40

Speed limit regions are stored in the `PurepursuitWaypointFollower`

class:

**Sources:** autopilot/purepursuitwaypointfollower.h109

Speed limit regions are defined in a GeoJSON FeatureCollection file following RFC 7946 (WGS-84 coordinate system).

| Requirement | Specification |
|---|---|
| Root type | Must be `"FeatureCollection"` |
| Geometry type | Must be `"Polygon"` (not MultiPolygon, LineString, etc.) |
| Coordinate order | `[longitude, latitude]` or `[longitude, latitude, altitude]` |
| Coordinate system | WGS-84 (implicit per RFC 7946) |
| maxSpeed property | Non-negative floating-point value in km/h |
| Coordinate ranges | Latitude: [-90, 90], Longitude: [-180, 180] |

**File Location:**
The system expects the file at `Documents/WayWise Speed Limits/speedLimitRegions.json`

. If the file is not found, instructional messages are printed to guide the user in creating it using https://geojson.io.

**Sources:** autopilot/purepursuitwaypointfollower.cpp570-598 autopilot/purepursuitwaypointfollower.cpp600-672

Speed limit regions undergo a coordinate transformation pipeline to convert from global WGS-84 coordinates to local ENU coordinates used by the autopilot.

**Code Implementation:**

**Why This Matters:**

`mVehicleState->getEnuRef()`

) must be set before loading speed limit regions.**Sources:** autopilot/purepursuitwaypointfollower.cpp640-666

During each autopilot update cycle, the vehicle's position is tested against all speed limit regions to determine which speed limits apply.

The speed limit enforcement occurs in the `updateControl()`

method:

**Key Behaviors:**

`std::min()`

.`isPointWithin()`

function operates in 2D (X-Y plane), ignoring altitude.**Sources:** autopilot/purepursuitwaypointfollower.cpp380-411

The following diagram shows how speed limits integrate with the Pure Pursuit control loop:

**Update Frequency:**
The speed limit check occurs every 50ms (20 Hz) as part of the Pure Pursuit update cycle, defined by `mUpdateStatePeriod_ms`

.

**Sources:** autopilot/purepursuitwaypointfollower.cpp380-411 autopilot/purepursuitwaypointfollower.h115

`loadSpeedLimitRegionsFile()`

Loads speed limit regions from a GeoJSON file. If the file cannot be opened, prints instructions for creating one using https://geojson.io.

**Parameters:**

`filePath`

: Path to the GeoJSON file**Example Usage:**

**Sources:** autopilot/purepursuitwaypointfollower.cpp570-598

`parseSpeedLimitRegionsDocument()`

Parses a GeoJSON document and extracts speed limit regions. Called internally by `loadSpeedLimitRegionsFile()`

.

**Validation Checks:**

`"FeatureCollection"`

`"Polygon"`

`maxSpeed`

property must be a valid non-negative number**Sources:** autopilot/purepursuitwaypointfollower.cpp600-672

`addSpeedLimitRegion()`

Adds a single speed limit region programmatically.

**Parameters:**

`boundary`

: List of polygon vertices in ENU coordinates (minimum 3 points required)`maxSpeed_kmph`

: Maximum speed in kilometers per hour (automatically converted to m/s)**Validation:**

**Example:**

**Sources:** autopilot/purepursuitwaypointfollower.cpp542-557

`clearSpeedLimitRegions()`

Removes all speed limit regions from the waypoint follower.

**Sources:** autopilot/purepursuitwaypointfollower.cpp559-563

`getSpeedLimitRegions()`

Returns a copy of all currently loaded speed limit regions.

**Returns:** List of `SpeedLimitRegion`

structures

**Sources:** autopilot/purepursuitwaypointfollower.cpp565-568

Speed limit regions are tightly integrated with the Pure Pursuit waypoint follower and affect control in the following ways:

**Priority:** Speed limit regions **override** the waypoint's specified speed if the vehicle is inside a region. The waypoint speed acts as an upper bound, and regions can only reduce it further, never increase it.

**Sources:** autopilot/purepursuitwaypointfollower.cpp383-390

Define speed limits around buildings or pedestrian areas:

Create zones with different speed limits for testing vehicle behavior:

| Zone | Purpose | Speed Limit |
|---|---|---|
| Acceleration zone | High-speed testing | 50 km/h |
| Handling zone | Cornering tests | 30 km/h |
| Precision zone | Low-speed maneuvers | 10 km/h |
| Safety zone | Emergency stop area | 5 km/h |

**Sources:** autopilot/purepursuitwaypointfollower.cpp574-579

| Limitation | Description |
|---|---|
2D Only | Altitude is ignored in point-in-polygon tests. Regions apply to all heights. |
No Holes | Inner boundaries or holes within polygons are not supported (only outer ring is processed). |
No MultiPolygon | Only single `Polygon` geometry type is supported, not `MultiPolygon` . |
Runtime Load Only | Regions must be loaded before starting route following; dynamic updates during operation are not supported. |
Global Minimum | Multiple overlapping regions always apply the most restrictive limit; weighted or prioritized limits are not possible. |

**Sources:** autopilot/purepursuitwaypointfollower.h38 autopilot/purepursuitwaypointfollower.cpp624-628

The speed limit region system depends on the following WayWise components:

| Component | Usage |
|---|---|
`VehicleState::getEnuRef()` | Provides ENU reference point for coordinate transformation |
`coordinateTransforms::llhToEnu()` | Converts WGS-84 to ENU coordinates |
`PosPoint` | Represents polygon vertices in ENU space |
`isPointWithin()` | Point-in-polygon algorithm (implementation not shown in provided files) |
`PurepursuitWaypointFollower::updateControl()` | Applies speed limits during control updates |

**Sources:** autopilot/purepursuitwaypointfollower.cpp640-666 autopilot/purepursuitwaypointfollower.cpp380-411

Refresh this wiki
