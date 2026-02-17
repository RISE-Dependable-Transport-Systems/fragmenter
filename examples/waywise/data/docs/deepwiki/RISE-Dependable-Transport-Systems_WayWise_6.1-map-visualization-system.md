# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/6.1-map-visualization-system

The Map Visualization System provides the central graphical display component for WayWise, rendering vehicles, routes, and geographic context on a 2D map. This document covers the `MapWidget`

class as the main visualization component, OpenStreetMap tile rendering via `OsmClient`

, interactive controls (pan, zoom, rotate), the `MapModule`

extension system for pluggable functionality, `TraceModule`

for path history visualization, and export capabilities (PDF, PNG).

For route planning and editing functionality that builds on top of the map, see Route Planning Interface. For vehicle state representation, see State Architecture & Position Sources. For coordinate system details, see Coordinate Systems & Transformations.

The Map Visualization System is built around a layered architecture where `MapWidget`

serves as the rendering canvas, `OsmClient`

provides geographic context through OpenStreetMap tiles, and a collection of `ObjectState`

instances represent vehicles and other entities. The `MapModule`

interface enables pluggable extensions to add features without modifying core code.

**Sources:** userinterface/map/mapwidget.h52-148 userinterface/map/mapwidget.cpp16-55 userinterface/map/mapwidget.h32-50

`MapWidget`

maintains the following key state variables for view control and rendering:

| Member Variable | Type | Purpose |
|---|---|---|
`mScaleFactor` | `double` | Zoom level (0.000001 to 20.0) |
`mRotation` | `double` | Map rotation in degrees |
`mXOffset` / `mYOffset` | `double` | Pan offset in scaled millimeters |
`mRefLlh` | `llh_t` | ENU reference point (lat/lon/height) |
`mObjectStateMap` | `QMap<int, QSharedPointer<ObjectState>>` | Vehicles and objects to display |
`mMapModules` | `QVector<QSharedPointer<MapModule>>` | Pluggable extensions |
`mFollowObjectId` | `int` | Object ID to follow (-1 = none) |
`mSelectedObject` | `int` | Currently selected object ID |

The default ENU reference is hardcoded to the RISE RTK base station location:

**Sources:** userinterface/map/mapwidget.h122-146 userinterface/map/mapwidget.cpp16-55

`MapWidget`

uses a two-stage coordinate transformation from local ENU coordinates to screen pixels:

The transformation is constructed in `paint()`

:

Note the Y-axis flip (`-mScaleFactor`

) to convert from mathematical ENU (Y up) to screen coordinates (Y down).

**Sources:** userinterface/map/mapwidget.cpp786-789 userinterface/map/mapwidget.cpp129-135

`MapWidget`

processes mouse and keyboard events to enable map navigation:

| Interaction | Action | Implementation |
|---|---|---|
Left Drag | Pan map | Updates `mXOffset` /`mYOffset` in `mouseMoveEvent()` |
Mouse Wheel / +/- keys | Zoom | Scales `mScaleFactor` in `wheelEvent()` |
Pinch Gesture | Zoom (touch) | Scales `mScaleFactor` in `event()` |
Ctrl+Shift+Click | Set ENU reference | Converts click position to LLH via `enuToLlh()` |
Right Click | Context menu | Delegates to `MapModule::populateContextMenu()` |

The wheel event implements zoom-to-cursor by adjusting offsets proportionally:

**Sources:** userinterface/map/mapwidget.cpp196-238 userinterface/map/mapwidget.cpp308-340 userinterface/map/mapwidget.cpp272-282

When `mFollowObjectId`

is set to a valid object ID, the map automatically centers on that vehicle each frame:

This creates a "chase camera" effect useful for monitoring a specific vehicle during operation.

**Sources:** userinterface/map/mapwidget.cpp758-765

`MapWidget`

delegates all OpenStreetMap tile operations to an `OsmClient`

instance (`mOsm`

). The client handles:

`osm_tiles/`

directory`QPixmap`

objects ready for renderingThe default configuration uses the RRZE FAU tile server:

Alternative servers can be set via `setTileServerUrl()`

.

**Sources:** userinterface/map/mapwidget.cpp31-51 userinterface/map/mapwidget.h137

The OSM zoom level is automatically calculated based on the current scale factor and ENU reference latitude:

The `cos(latitude)`

term compensates for the Mercator projection's distortion at different latitudes. The zoom level is clamped to the range [0, `mOsmMaxZoomLevel`

] (default max: 19).

**Sources:** userinterface/map/mapwidget.cpp664-670

The `drawOSMTiles()`

method implements a viewport-based tile rendering strategy:

The algorithm converts the ENU reference point to OSM tile coordinates, then renders a 40×40 grid of tiles, culling those outside the viewport. Missing tiles are queued for asynchronous download if the download queue is not full.

**Sources:** userinterface/map/mapwidget.cpp658-727 userinterface/map/mapwidget.cpp672-721

OpenStreetMap uses a specific tile coordinate system where each zoom level doubles the number of tiles. The conversion from geographic coordinates (latitude/longitude) to tile coordinates is performed by `OsmTile`

static methods:

`OsmTile::long2tilex(longitude, zoom)`

- Longitude to tile X`OsmTile::lat2tiley(latitude, zoom)`

- Latitude to tile Y`OsmTile::tilex2long(x, zoom)`

- Tile X to longitude`OsmTile::tiley2lat(y, zoom)`

- Tile Y to latitudeOnce tile coordinates are known, they are converted to ENU coordinates via `coordinateTransforms::llhToEnu()`

for rendering.

**Sources:** userinterface/map/mapwidget.cpp672-677

`MapWidget`

maintains a `QMap<int, QSharedPointer<ObjectState>>`

to track all displayable objects (vehicles, trailers, etc.). Objects are added via `addObjectState()`

, which also connects to the object's `positionUpdated()`

signal to trigger automatic repaints:

This ensures the map automatically updates when any vehicle's position changes.

**Sources:** userinterface/map/mapwidget.cpp57-65

During the `paint()`

method, all objects are rendered after the map background, grid, and module content:

The `draw()`

method is implemented by each `ObjectState`

subclass (`VehicleState`

, `CarState`

, `TruckState`

, `CopterState`

) to render vehicle-specific graphics. The selected object receives a `true`

flag for highlighted rendering.

**Sources:** userinterface/map/mapwidget.cpp829-832

The coordinate grid provides visual reference with dynamically scaling grid lines and numeric labels:

The grid step size is automatically calculated to maintain readable spacing as the user zooms:

This algorithm produces step sizes like 1m, 2m, 5m, 10m, 20m, 50m, etc., depending on zoom level. The zero axes (X=0 and Y=0) are drawn in red with increased width.

**Sources:** userinterface/map/mapwidget.cpp540-656 userinterface/map/mapwidget.cpp547-556

The `MapModule`

abstract class defines three virtual methods for pluggable functionality:

Modules are added via `addMapModule()`

and automatically receive callbacks during rendering and event processing. If `processMouse()`

returns `true`

, event propagation stops, allowing modules to "consume" events.

**Sources:** userinterface/map/mapwidget.h32-50

`MapWidget`

delegates to modules at specific points in the rendering and event pipeline:

| Integration Point | Method | Purpose |
|---|---|---|
Rendering | `processPaint()` | Draw module-specific graphics between grid and vehicles |
Mouse Press | `processMouse(isPress=true, ...)` | Handle click/drag start |
Mouse Release | `processMouse(isRelease=true, ...)` | Handle click/drag end |
Mouse Move | `processMouse(isMove=true, ...)` | Handle hover/drag |
Mouse Wheel | `processMouse(isWheel=true, ...)` | Handle zoom/scroll |
Right Click | `populateContextMenu()` | Add menu items |

Modules are processed in order of addition, allowing layered functionality.

**Sources:** userinterface/map/mapwidget.cpp196-323 userinterface/map/mapwidget.cpp820-826 userinterface/map/mapwidget.cpp249-258

The WayWise codebase includes several `MapModule`

implementations:

**Sources:** userinterface/map/tracemodule.h14-45

`TraceModule`

records and displays vehicle position history for multiple position sources simultaneously. It tracks up to 6 position types:

| PosType | Color (Default) | Purpose |
|---|---|---|
`simulated` | Blue | Simulated/commanded positions |
`fused` | Red | Sensor-fused estimate |
`odom` | (inactive) | Odometry-based dead reckoning |
`IMU` | (inactive) | IMU-based estimate |
`GNSS` | Magenta | Raw GNSS position |
`UWB` | (inactive) | Ultra-wideband positioning |

Only `simulated`

, `fused`

, and `GNSS`

are active by default. Each type can be enabled/disabled and colored independently via `setTraceActiveForPosType()`

and `setTraceColorForPosType()`

.

**Sources:** userinterface/map/tracemodule.cpp7-16 userinterface/map/tracemodule.h33-39

Traces are recorded by a timer-based sampling system:

The timer fires every `mTraceSampleTimerPeriod_ms`

(default 100ms) and samples all active position types. Points are only added if the distance from the last point exceeds `minTraceSampleDistance`

(default 0.1m), preventing excessive data accumulation during standstill.

**Sources:** userinterface/map/tracemodule.cpp18-36 userinterface/map/tracemodule.h40-43

`TraceModule`

supports multiple independent trace sequences via `currentTraceIndex`

:

This three-level structure enables:

Traces can be started with `startTrace(index)`

, switched with `setCurrentTraceIndex(index)`

, and cleared with `clearTraceIndex(index)`

. This allows comparing multiple runs or recording different phases of operation separately.

**Sources:** userinterface/map/tracemodule.h43 userinterface/map/tracemodule.cpp79-95 userinterface/map/tracemodule.cpp107-113

The `processPaint()`

method draws all traces as connected line segments:

The pen width is scaled inversely with map scale (`7.5/scale`

) to maintain constant visual thickness regardless of zoom level.

**Sources:** userinterface/map/tracemodule.cpp39-62 userinterface/map/tracemodule.cpp44

`MapWidget`

can export the current map view to a PDF file via `printPdf()`

:

The export uses Qt's `QPrinter`

with a custom page layout that eliminates margins and sets exact dimensions. The `highQuality=true`

flag enables full antialiasing for publication-quality output.

**Sources:** userinterface/map/mapwidget.cpp426-455

Raster image export is provided via `printPng()`

:

This creates a `QImage`

of the specified dimensions, renders the map into it with high quality settings, and saves to disk. Default dimensions match the widget's current size if not specified.

**Sources:** userinterface/map/mapwidget.cpp457-471

Both export methods preserve:

This enables generating reports, documentation, or archival records of vehicle operations.

Refresh this wiki
