# Source: https://deepwiki.com/das-rise/WayWise/8.1-zigzag-route-generator

The `ZigZagRouteGenerator`

class provides a set of static geometric utilities designed to automate the creation of coverage paths within convex polygons. It handles the transformation of a boundary defined by `PosPoint`

objects into a systematic "zigzag" (lawnmower) pattern, with support for perimeter framing, speed transitions, and attribute-based distance stamping.

The generator operates primarily on ENU (East-North-Up) coordinates. It determines the optimal traversal direction by identifying the "baseline" of a convex polygon that results in the minimum height, thereby minimizing the number of turns required to cover the area.

To generate an efficient path, the algorithm first identifies the best edge of the polygon to serve as the orientation reference.

`getBaselineDeterminingMinHeightOfConvexPolygon`

iterates through every edge of the polygon and calculates the maximum perpendicular distance from that edge to any other vertex in the polygon routeplanning/zigzagroutegenerator.cpp141-165 The edge that yields the smallest "maximum distance" is selected as the baseline to ensure the shortest possible zigzag segments.`getConvexPolygonOrientation`

is used to determine if the vertices are provided in clockwise or counter-clockwise order, which influences the sign of the normal vectors used to offset the zigzag lines routeplanning/zigzagroutegenerator.cpp181-184The primary entry point for generation is `fillConvexPolygonWithZigZag`

routeplanning/zigzagroutegenerator.cpp167-169

`spacing`

parameter.`getAllIntersections`

routeplanning/zigzagroutegenerator.cpp94-108`keepTurnsInBounds`

is true, the turn-around points are clipped to the polygon perimeter.The `fillConvexPolygonWithFramedZigZag`

method extends the standard fill by first generating a perimeter pass (a "frame") before starting the internal zigzag pattern routeplanning/zigzagroutegenerator.h26-27 This is often used in agricultural or industrial applications to ensure the boundaries are fully covered before the main traversal begins.

**Sources:** routeplanning/zigzagroutegenerator.cpp141-184 routeplanning/zigzagroutegenerator.h12-33

The following diagram maps the natural language requirements of route planning to the specific C++ entities within the `routeplanning`

module.

Title: ZigZag Generation Sequence

**Sources:** routeplanning/zigzagroutegenerator.cpp141-165 routeplanning/zigzagroutegenerator.cpp167-184 routeplanning/zigzagroutegenerator.h12-29

The generator supports "stamping" specific bitmask attributes onto the `PosPoint`

objects based on their location relative to turns.

`setAttributesOnStraights`

) and the turn-around points (`setAttributesInTurns`

) routeplanning/zigzagroutegenerator.h24-25`attributeDistanceAfterTurn`

and `attributeDistanceBeforeTurn`

allow the "straight" attributes to be delayed or ended early, providing a safety buffer where the vehicle transitions its state (e.g., turning off a sprayer or tool before entering a turn) routeplanning/zigzagroutegenerator.cpp168-169The `visitEveryX`

parameter allows for skipping parallel lines. If set to 1, every line is visited. If set to a higher integer, the generator skips lines, which is useful for multi-pass operations or vehicles with wide implements that require overlapping patterns generated in separate missions routeplanning/zigzagroutegenerator.h24-27

The class relies on several internal geometric helpers:

`lineIntersect`

`ccw`

) method to determine if two line segments cross routeplanning/zigzagroutegenerator.cpp56-65`getLineIntersection`

`PosPoint`

where two infinite lines defined by segments intersect routeplanning/zigzagroutegenerator.cpp80-92`getShrinkedConvexPolygon`

The `ZigZagRouteGenerator`

works in conjunction with `RouteUtils`

for file I/O and containment checks.

Title: Route Planning Module Dependencies

**Sources:** routeplanning/zigzagroutegenerator.h12-33 routeplanning/routeutils.h19-21 core/pospoint.cpp1-10

While the generator produces the `QList<PosPoint>`

, it is typically consumed by the `PurepursuitWaypointFollower`

or similar autopilot components. The generated `speed`

and `speedInTurns`

parameters are baked into the `PosPoint`

objects, allowing the vehicle to automatically slow down during maneuvers routeplanning/zigzagroutegenerator.cpp167-169

**Sources:** autopilot/purepursuitwaypointfollower.cpp1-20 routeplanning/zigzagroutegenerator.cpp167-169

Refresh this wiki

This wiki was recently refreshed. Please wait 6 days to refresh again.