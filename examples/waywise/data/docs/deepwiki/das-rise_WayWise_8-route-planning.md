# Source: https://deepwiki.com/das-rise/WayWise/8-route-planning

The Route Planning module provides the computational and visual tools necessary to define vehicle paths. It transitions from raw geometric boundaries to executable mission routes composed of `PosPoint`

sequences. This module includes algorithms for coverage path planning (specifically for convex polygons), file-based route persistence, and a dedicated user interface for interactive route generation.

The route planning subsystem is structured as a pipeline: the user defines a boundary via the UI, a generator algorithm calculates the optimal path, and utility functions handle the transformation and storage of the resulting waypoints.

**Route Planning Flow**

Sources: userinterface/routegeneratorui.h18-43 routeplanning/zigzagroutegenerator.h12-33 routeplanning/routeutils.h19-21

The `ZigZagRouteGenerator`

is the primary engine for automated path creation. It specializes in filling convex polygons with efficient "S-curve" or "zigzag" patterns, commonly used for agricultural coverage or area surveillance.

Key capabilities include:

`PosPoint`

objects, such as different speeds or bitmask attributes for "straights" vs "turns" routeplanning/zigzagroutegenerator.cpp167-169For details, see ZigZag Route Generator.

`RouteUtils`

provides a collection of shared geometric helpers and I/O functions that bridge the gap between local ENU coordinates and global LLH coordinates during route import/export.

| Function | Purpose |
|---|---|
`readRouteFromFile` | Parses XML route files and transforms coordinates based on a vehicle's ENU reference routeplanning/routeutils.cpp7-79 |
`isPointWithin` | Determines if a specific coordinate lies inside a closed path (polygon) routeplanning/routeutils.cpp81-105 |

Sources: routeplanning/routeutils.h19-21 routeplanning/routeutils.cpp7-105

The user interface components provide an interactive environment for planning. The `RouteGeneratorUI`

serves as a container that hosts specific generator widgets and a preview map.

`MapWidget`

and a `QTabWidget`

for different generation algorithms userinterface/routegeneratorui.cpp9-25`MapWidget`

that handles the logic for drawing boundaries and displaying generated routes userinterface/routegeneratorui.h43For details, see Route Planning UI.

This diagram maps high-level planning concepts to the specific classes and files implementing them.

**Planning Entity Map**

Sources: userinterface/routegeneratorui.h23-24 routeplanning/zigzagroutegenerator.h12-13 routeplanning/routeutils.h19

Refresh this wiki

This wiki was recently refreshed. Please wait 6 days to refresh again.