# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/6.2-route-planning-interface

The Route Planning Interface provides interactive tools for creating, editing, and managing navigation routes for autonomous vehicles. This system consists of the `PlanUI`

widget and the `RoutePlannerModule`

map extension, which together enable graphical route creation through map interaction, multi-route management, and XML-based route persistence.

For information about route file formats and coordinate transformations, see Route Generation Tools. For details on how routes are consumed by autopilot systems, see Waypoint Follower Interface and Pure Pursuit Waypoint Follower.

The route planning system consists of two primary components that work together:

**Sources:** userinterface/planui.h8-84 userinterface/map/routeplannermodule.h8-69

`PlanUI`

is a Qt widget that provides the user interface controls for route planning. It manages the overall route planning workflow and user interactions.

| Component | Type | Purpose |
|---|---|---|
`mRoutePlanner` | `QSharedPointer<RoutePlannerModule>` | Map module for interactive route editing |
`mRouteGeneratorUI` | `QSharedPointer<RouteGeneratorUI>` | Dialog for algorithmic route generation |
`mCurrentVehicleConnection` | `QSharedPointer<VehicleConnection>` | Link to vehicle for route upload/download |

**Sources:** userinterface/planui.h76-81 userinterface/planui.cpp8-32

`RoutePlannerModule`

extends `MapModule`

to add interactive route editing capabilities directly on the map display. It handles mouse events, rendering, and route data management.

| Property | Type | Purpose |
|---|---|---|
`mRoutes` | `QList<QList<PosPoint>>` | Storage for multiple routes |
`mPlannerState.currentRouteIndex` | `int` | Index of currently selected route |
`mPlannerState.currentPointIndex` | `int` | Index of point being dragged (-1 if none) |
`mPlannerState.newPointHeight` | `double` | Default height for new points (meters) |
`mPlannerState.newPointSpeed` | `double` | Default speed for new points (m/s) |
`mPlannerState.newPointAttribute` | `uint32_t` | Default attribute flags for new points |
`mPlannerState.updatePointOnClick` | `bool` | Whether to update existing points on click |

**Sources:** userinterface/map/routeplannermodule.h49-59 userinterface/map/routeplannermodule.cpp7-38

The `RoutePlannerModule`

processes mouse events to enable direct route creation and modification on the map through keyboard modifiers and mouse buttons.

**Sources:** userinterface/map/routeplannermodule.cpp50-132

When adding a new point, the module determines the optimal insertion location based on distance heuristics:

The module detects clicks on existing points by calculating the pixel distance threshold:

**Sources:** userinterface/map/routeplannermodule.cpp50-132

Each waypoint in a route is represented by a `PosPoint`

structure with the following configurable parameters:

| Parameter | UI Control | Range/Format | Notes |
|---|---|---|---|
| X, Y Position | Map Click | ENU coordinates (meters) | Derived from click location |
| Height (Z) | `heightSpinBox` | Meters | Altitude above ENU reference |
| Speed | `speedSpinBox` | km/h (converted to m/s) | Desired speed at waypoint |
| Attributes | `attributeLineEdit` | 32-bit hex value | Custom flags for autopilot |

The UI provides a checkbox to control whether clicking on existing points updates them with current parameter values or enters drag mode.

**Sources:** userinterface/planui.cpp76-95 userinterface/planui.ui177-241

The system maintains a collection of routes (`QList<QList<PosPoint>>`

) and allows switching between them. The UI displays the current route index and total count.

**Sources:** userinterface/planui.cpp65-68 userinterface/map/routeplannermodule.cpp134-139

| Operation | Button | Implementation | Effect |
|---|---|---|---|
| Add Route | `addRouteButton` | `addNewRoute()` | Appends empty route, switches to it |
| Remove Route | `removeRouteButton` | `removeCurrentRoute()` | Deletes current route (minimum 1 retained) |
| Import Route | `importRouteButton` | `readRouteFromFile()` | Loads XML file, adds to collection |
| Export Current | `exportCurrentRouteButton` | `xmlStreamWriteRoute()` | Saves current route with ENU ref |
| Export All | `exportAllRoutesButton` | Iterates all routes | Saves multi-route XML file |

**Sources:** userinterface/planui.cpp49-63 userinterface/planui.cpp121-190

The interface provides three operations to modify the structure of the current route:

Inverts the order of all points in the current route. Useful for creating return paths.

**Sources:** userinterface/map/routeplannermodule.cpp358-366 userinterface/planui.cpp215-218

Merges the current route onto the end of another route, then removes the current route from the collection.

**User Interaction Flow:**

**Sources:** userinterface/planui.cpp220-235 userinterface/map/routeplannermodule.cpp368-375

Divides the current route into two separate routes at a selected connection point.

The split button is dynamically enabled/disabled based on route size (minimum 2 points required).

**Sources:** userinterface/planui.cpp237-259 userinterface/map/routeplannermodule.cpp377-384

The `RoutePlannerModule`

renders routes on the map with different visual styles to indicate selection state and point metadata.

**Sources:** userinterface/map/routeplannermodule.cpp41-47 userinterface/map/routeplannermodule.cpp253-356

| Element | Selected Route | Inactive Route |
|---|---|---|
| Line color | Dark yellow | Dark gray |
| Point fill | Yellow | Gray |
| Point border width | 3.0 / scale | 3.0 / scale |
| Point radius | 10.0 / scale | 10.0 / scale |
| First point marker | Green dot (5px radius) | None |
| Last point marker | Red dot (5px radius) | None |
| Text annotations | Position, speed, attributes | Route ID only |

The rendering system supports two quality modes:

`drawEllipse()`

with antialiasing (routeplannermodule.cpp286-299)`drawCircleFast()`

(routeplannermodule.cpp301)**Sources:** userinterface/map/routeplannermodule.cpp253-356

Routes are saved to and loaded from XML files with an embedded ENU reference coordinate.

The `PlanUI`

class implements XML serialization using `QXmlStreamWriter`

and deserialization using helper functions from `RouteUtils`

.

**Export Functions:**

`xmlStreamWriteRoute()`

- Writes a single route (planui.cpp97-110)`xmlStreamWriteEnuRef()`

- Writes ENU reference with maximum precision (49 significant figures) (planui.cpp112-119)**Export Workflow:**

`QXmlStreamWriter`

creates UTF-8 encoded, auto-formatted XML**Import Workflow:**

`readRouteFromFile()`

parses XML and transforms coordinates**Sources:** userinterface/planui.cpp97-208 routeplanning/routeutils.h

The route planning interface integrates with the vehicle communication system to enable bidirectional route transfer.

**Sources:** userinterface/planui.h34 userinterface/planui.cpp261-279

When the user clicks "Send to Autopilot", `PlanUI`

emits the `routeDoneForUse`

signal with the current route:

This signal is typically connected to vehicle-specific UI components (e.g., `DriveUI`

, `FlyUI`

) that forward the route to the vehicle through their `VehicleConnection`

instance.

**Sources:** userinterface/planui.cpp70-74

The "Download Route from Vehicle" button requests the currently loaded route from the vehicle's autopilot system:

`mCurrentVehicleConnection`

is set (planui.cpp265)`mCurrentVehicleConnection->requestCurrentRouteFromVehicle()`

(planui.cpp270)This allows users to inspect and modify routes that are currently active on the vehicle.

**Sources:** userinterface/planui.cpp268-279

`PlanUI`

integrates with `RouteGeneratorUI`

to provide algorithmic route generation capabilities (e.g., zigzag patterns for area coverage).

The connection is established in the constructor, where `PlanUI`

connects the `RouteGeneratorUI::routeDoneForUse`

signal to a lambda that handles route addition logic.

**Sources:** userinterface/planui.cpp14-26 userinterface/planui.cpp210-213

| Class | File | Purpose |
|---|---|---|
`PlanUI` | userinterface/planui.h userinterface/planui.cpp | Main widget providing route planning controls |
`RoutePlannerModule` | userinterface/map/routeplannermodule.h userinterface/map/routeplannermodule.cpp | `MapModule` for interactive route editing on map |
`RouteGeneratorUI` | userinterface/routegeneratorui.h | Dialog for algorithmic route generation |

| Method | Class | Purpose |
|---|---|---|
`processMouse()` | `RoutePlannerModule` | Handles mouse events for route interaction |
`processPaint()` | `RoutePlannerModule` | Renders routes on map |
`xmlStreamWriteRoute()` | `PlanUI` | Serializes route to XML format |
`readRouteFromFile()` | `RouteUtils` | Deserializes route from XML |
`reverseCurrentRoute()` | `RoutePlannerModule` | Reverses point order |
`splitCurrentRouteAt()` | `RoutePlannerModule` | Splits route into two |
`appendCurrentRouteTo()` | `RoutePlannerModule` | Merges routes |

**Sources:** userinterface/planui.h userinterface/map/routeplannermodule.h

Refresh this wiki
