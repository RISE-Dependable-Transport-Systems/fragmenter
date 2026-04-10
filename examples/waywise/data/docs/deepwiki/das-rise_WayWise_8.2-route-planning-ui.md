# Source: https://deepwiki.com/das-rise/WayWise/8.2-route-planning-ui

The Route Planning UI subsystem provides the graphical tools necessary for creating, editing, and generating vehicle missions. It consists of a `MapWidget`

plugin for manual interaction, specialized dialogs for algorithmic route generation (such as zig-zags for area coverage), and a primary management panel (`PlanUI`

) for handling multiple routes and vehicle synchronization.

The route planning logic is distributed between interactive map modules and configuration widgets. The `PlanUI`

acts as the central coordinator, bridging the `RoutePlannerModule`

(the visual backend) with the `RouteGeneratorUI`

(the algorithmic frontend).

This diagram illustrates how user interface components relate to the underlying route planning logic.

**Sources:** userinterface/planui.h26-82 userinterface/map/routeplannermodule.h13-67 userinterface/routegeneratorui.h18-69 userinterface/routegeneratorzigzagui.h18-60

`RoutePlannerModule`

is a specialized `MapModule`

userinterface/map/routeplannermodule.h13 that implements the drawing and mouse interaction logic for routes on the `MapWidget`

. It supports multiple routes, where one is active for editing at any given time userinterface/map/routeplannermodule.h50

`Shift + Left Click`

and remove them with `Shift + Right Click`

userinterface/map/routeplannermodule.cpp76-127The module pre-renders pixmaps for different point states (Default, Inactive) to ensure high performance during map repaints userinterface/map/routeplannermodule.cpp10-35

**Sources:** userinterface/map/routeplannermodule.cpp41-132 userinterface/map/routeplannermodule.h43-66

The `RouteGeneratorUI`

is a container dialog that hosts different route generation algorithms userinterface/routegeneratorui.cpp24 Currently, it primarily supports the ZigZag generator.

This widget provides a two-step workflow for generating area-coverage patterns:

| Parameter | Function | Source |
|---|---|---|
`rowSpacing` | Distance between parallel passes in meters | userinterface/routegeneratorzigzagui.cpp87-91 |
`speedStraights` | Target speed for straight segments (km/h) | userinterface/routegeneratorzigzagui.cpp73-77 |
`speedTurns` | Reduced speed during turn maneuvers (km/h) | userinterface/routegeneratorzigzagui.cpp80-84 |
`visitEveryX` | Skips rows to accommodate large turning radii | userinterface/routegeneratorzigzagui.cpp94-98 |

**Sources:** userinterface/routegeneratorui.cpp9-25 userinterface/routegeneratorzigzagui.cpp52-71

`PlanUI`

is the primary sidebar panel for managing mission life cycles userinterface/planui.ui4 It coordinates the storage of multiple routes and their synchronization with vehicles.

`routeDoneForUse`

signal containing a `QList<PosPoint>`

when the "Send to Autopilot" button is clicked userinterface/planui.cpp70-74This diagram shows how a route moves from generation to the vehicle.

**Sources:** userinterface/planui.cpp16-26 userinterface/routegeneratorzigzagui.cpp52-71 userinterface/routegeneratorui.cpp47-52

Routes are saved in an XML format that captures both the spatial data and the logical attributes of each point.

`<enuref>`

tag to define the local coordinate origin userinterface/planui.cpp112-119`<point>`

includes `x`

, `y`

, `z`

(height), `speed`

, and `attributes`

(hexadecimal bitmask) userinterface/planui.cpp99-109**Sources:** userinterface/planui.cpp97-120 userinterface/planui.h79-80

Refresh this wiki

This wiki was recently refreshed. Please wait 6 days to refresh again.