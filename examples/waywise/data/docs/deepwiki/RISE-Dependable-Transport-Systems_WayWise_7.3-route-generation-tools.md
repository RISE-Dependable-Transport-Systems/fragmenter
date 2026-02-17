# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/7.3-route-generation-tools

This page documents the automated route generation capabilities in WayWise, focusing on the `ZigZagRouteGenerator`

class and associated utility functions. These tools generate systematic coverage patterns for vehicles to follow within defined boundary polygons, commonly used for surveying, inspection, or area coverage missions.

For information about how routes are edited interactively in the UI, see Route Planning Interface. For details on the `PosPoint`

structure used to represent waypoints, see Position Types & PosPoint Structure. For coordinate system conversions between route representations, see Coordinate Systems & Transformations.

The route generation system provides:

These tools are used by `RouteGeneratorUI`

to provide automated route creation in the planning interface and can be invoked programmatically for batch route generation.

The route generation system consists of two main components: `ZigZagRouteGenerator`

for pattern generation and `routeutils`

for file operations and geometric validation.

**Sources:** routeplanning/zigzagroutegenerator.h1-36 routeplanning/routeutils.h1-23

The `ZigZagRouteGenerator`

class provides static methods for generating systematic coverage patterns. It is a utility class with a protected constructor, designed to be used through its static interface.

| Method | Purpose | Returns |
|---|---|---|
`fillConvexPolygonWithZigZag()` | Generate zigzag pattern within polygon | `QList<PosPoint>` |
`fillConvexPolygonWithFramedZigZag()` | Generate boundary-first zigzag pattern | `QList<PosPoint>` |
`getBaselineDeterminingMinHeightOfConvexPolygon()` | Find optimal zigzag direction | `QPair<PosPoint, PosPoint>` |
`getShrinkedConvexPolygon()` | Create inset polygon | `QList<PosPoint>` |
`getConvexPolygonOrientation()` | Determine polygon winding direction | `int` (+1 or -1) |
`getAllIntersections()` | Find all route/polygon intersections | `QList<PosPoint>` |
`getLineIntersection()` | Compute intersection point of two lines | `PosPoint` |
`lineIntersect()` | Check if two line segments intersect | `bool` |
`intersectionExists()` | Check for any intersection between routes | `bool` |
`distanceToLine()` | Calculate perpendicular distance to line | `double` |
`ccw()` | Counter-clockwise orientation test | `bool` |
`getClosestPointInRoute()` | Find nearest waypoint to reference | `int` (index) |

**Sources:** routeplanning/zigzagroutegenerator.h12-33

The primary route generation method is `fillConvexPolygonWithZigZag()`

, which creates a systematic back-and-forth coverage pattern.

**Sources:** routeplanning/zigzagroutegenerator.cpp167-392

The algorithm finds the optimal zigzag direction by selecting the polygon edge that minimizes the polygon's "height" (maximum perpendicular distance from any vertex to that edge).

routeplanning/zigzagroutegenerator.cpp141-165

This ensures the zigzag lines are aligned with the polygon's dominant orientation, minimizing turn count.

Starting from the baseline, parallel lines are drawn at `spacing`

intervals perpendicular to the baseline direction.

routeplanning/zigzagroutegenerator.cpp180-194

The algorithm:

Each parallel line is trimmed to the polygon boundaries using line-line intersection calculations.

routeplanning/zigzagroutegenerator.cpp80-92

The intersection point is computed using the formula:

When `turnIntermediateSteps > 0`

, the algorithm inserts intermediate waypoints to create smooth circular turns.

routeplanning/zigzagroutegenerator.cpp246-362

Turn generation:

`visitEveryX`

mode)`spacing/2`

for single-pass, `visitEveryX * spacing/2`

for multi-pass**Sources:** routeplanning/zigzagroutegenerator.cpp167-392

The `fillConvexPolygonWithZigZag()`

method accepts extensive configuration:

| Parameter | Type | Purpose |
|---|---|---|
`bounds` | `QList<PosPoint>` | Convex polygon vertices defining coverage area |
`spacing` | `double` | Distance between parallel zigzag lines (meters) |
`keepTurnsInBounds` | `bool` | Ensure turn arcs stay within polygon |
`speed` | `double` | Speed for straight segments (m/s) |
`speedInTurns` | `double` | Speed for turn segments (m/s) |
`turnIntermediateSteps` | `int` | Number of waypoints per turn (0 = sharp corners) |
`visitEveryX` | `int` | Skip pattern for multi-pass coverage (0 = single pass) |
`setAttributesOnStraights` | `uint32_t` | Bit flags to set on straight segments |
`setAttributesInTurns` | `uint32_t` | Bit flags to set on turn segments |
`attributeDistanceAfterTurn` | `double` | Distance from turn end to attribute change |
`attributeDistanceBeforeTurn` | `double` | Distance from turn start to attribute change |

**Sources:** routeplanning/zigzagroutegenerator.h24-25

The `fillConvexPolygonWithFramedZigZag()`

method generates a route that first traces the polygon boundary, then fills the interior with a zigzag pattern.

routeplanning/zigzagroutegenerator.cpp394-415

This variant is useful for:

**Sources:** routeplanning/zigzagroutegenerator.cpp394-415

The `getShrinkedConvexPolygon()`

method creates an inset polygon by shifting each edge inward by a specified distance.

routeplanning/zigzagroutegenerator.cpp417-436

The shrinking operation:

`spacing`

**Sources:** routeplanning/zigzagroutegenerator.cpp417-436

The `lineIntersect()`

method uses the CCW (counter-clockwise) test to determine if two line segments intersect.

routeplanning/zigzagroutegenerator.cpp62-65

Two segments intersect if:

The CCW test routeplanning/zigzagroutegenerator.cpp56-60 determines orientation using the cross product sign:

The `distanceToLine()`

method calculates the perpendicular distance from a point to a line segment.

routeplanning/zigzagroutegenerator.cpp13-54

Algorithm:

This is used in baseline determination to find the polygon edge with minimum height.

The `getConvexPolygonOrientation()`

method determines if a polygon's vertices are ordered clockwise or counter-clockwise.

routeplanning/zigzagroutegenerator.cpp438-446

Returns:

`+1`

: Counter-clockwise winding`-1`

: Clockwise windingThe orientation is computed using the signed area formula with the first three vertices.

**Sources:** routeplanning/zigzagroutegenerator.cpp13-65 routeplanning/zigzagroutegenerator.cpp438-446

The `routeutils`

module provides file I/O functions for route persistence and exchange.

Routes are stored in XML format with ENU reference information for coordinate transformation:

The `readRouteFromFile()`

function loads a route and transforms it to the vehicle's ENU reference.

routeplanning/routeutils.cpp7-79

The transformation process:

This allows routes created with one ENU reference to be used by vehicles with different ENU references, enabling route sharing and reuse.

**Sources:** routeplanning/routeutils.cpp7-79

The `isPointWithin()`

function uses the ray casting algorithm to determine if a point lies within a polygon.

routeplanning/routeutils.cpp81-107

Algorithm:

This is used for:

**Sources:** routeplanning/routeutils.cpp81-107

The route generation tools are included in all example applications:

| Example | CMakeLists Reference |
|---|---|
| RCCar_ISO22133_autopilot | examples/RCCar_ISO22133_autopilot/CMakeLists.txt53-54 |
| RCCar_MAVLINK_autopilot | examples/RCCar_MAVLINK_autopilot/CMakeLists.txt52-53 |
| map_local_twocars | examples/map_local_twocars/CMakeLists.txt49-50 |

Both `routeutils.cpp`

and `routeutils.h`

are compiled into each application.

**Note:** While `zigzagroutegenerator.cpp`

is not listed in the CMakeLists files, it would need to be added if zigzag generation is required. The class header is referenced by `routeutils.h`

.

The route generation tools integrate with the route planning UI:

`ZigZagRouteGenerator::fillConvexPolygonWithZigZag()`

generates waypoints`PlanUI`

for display and editing`MultiWaypointFollower`

Typical parameter values for different vehicle types:

| Vehicle Type | Spacing | Speed (straight) | Speed (turns) | Turn Steps |
|---|---|---|---|---|
| Ground rover | 2-5 m | 1-3 m/s | 0.5-1 m/s | 3-5 |
| Survey drone | 10-30 m | 5-10 m/s | 3-5 m/s | 5-10 |
| Inspection drone | 1-3 m | 1-2 m/s | 0.5-1 m/s | 5-8 |

**Sources:** All CMakeLists files, general system architecture

The route generation tools provide a robust foundation for automated mission planning in WayWise. By combining geometric algorithms with configurable parameters and coordinate transformations, they enable flexible coverage pattern generation for diverse vehicle platforms and mission requirements.

Refresh this wiki
