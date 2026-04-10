# Source: https://deepwiki.com/das-rise/WayWise/9.1-map-widget-and-osm-integration

The `MapWidget`

is the primary visualization component of the WayWise user interface. It provides a 2D coordinate-aware canvas that renders geographic data (OpenStreetMap), vehicle states, and planned routes. It utilizes a plugin-based architecture via the `MapModule`

interface to allow modular extensions like path history (tracing) and route planning.

The `MapWidget`

class is a `QWidget`

that performs custom painting using `QPainter`

. It manages a local coordinate system based on an **ENU (East-North-Up)** reference point, allowing high-precision local rendering while maintaining global geographic context.

The widget maintains a transformation pipeline that converts internal millimeter-based coordinates to screen pixels.

`llh_t`

coordinate (latitude, longitude, height) userinterface/map/mapwidget.h125`ObjectState`

by ID, automatically updating the `mXOffset`

and `mYOffset`

to keep the vehicle centered userinterface/map/mapwidget.cpp180-188The `paintEvent`

triggers a sequence of drawing operations:

`MapModule`

instances and calls their `processPaint`

functions userinterface/map/mapwidget.cpp145`ObjectState`

instances registered via `addObjectState`

userinterface/map/mapwidget.cpp57-65The following diagram illustrates how vehicle data flows from the core logic to the visual representation in `MapWidget`

.

**Vehicle Rendering Data Flow**

Sources: userinterface/map/mapwidget.h52-148 userinterface/map/mapwidget.cpp57-65 userinterface/map/mapwidget.cpp191-194

WayWise integrates OSM tiles for background context. This is handled by the `OsmClient`

and `OsmTile`

classes.

`http://c.osm.rrze.fau.de/osmhd`

) userinterface/map/mapwidget.cpp48`osm_tiles`

directory to reduce network load and allow offline use userinterface/map/mapwidget.cpp46`mScaleFactor`

userinterface/map/mapwidget.cpp33-35Tiles are drawn in `drawOSMTiles`

. The system calculates which tile indices (X, Y) are visible within the current viewport and requests them from `OsmClient`

. If a tile is not in cache, it is downloaded asynchronously, and the `tileReady`

signal triggers a widget repaint userinterface/map/mapwidget.cpp149-153

Sources: userinterface/map/mapwidget.cpp31-52 userinterface/map/mapwidget.cpp119

The `MapModule`

class is an abstract interface that allows external components to hook into the `MapWidget`

's event loop and rendering pipeline without modifying the widget's core code.

| Function | Description |
|---|---|
`processPaint` | Called during the widget's paint event. Provides the `QPainter` and current transformations. |
`processMouse` | Handles mouse clicks, movement, and wheel events. Can return `true` to "consume" the event. |
`populateContextMenu` | Allows the module to add custom actions to the map's right-click menu. |

Sources: userinterface/map/mapwidget.h32-50

The `TraceModule`

is a concrete implementation of `MapModule`

used to visualize the historical path of a vehicle. It supports multiple position types (Simulated, GNSS, Fused) simultaneously.

`QTimer`

(`mTraceSampleTimer`

) to sample the vehicle's position at a configurable interval (default 100ms) userinterface/map/tracemodule.cpp18-35`minTraceSampleDistance`

(default 0.1m) userinterface/map/tracemodule.cpp29-30`PosType`

values, allowing the UI to show the discrepancy between raw GNSS and fused positioning userinterface/map/tracemodule.cpp50-61**TraceModule Logic**

Sources: userinterface/map/tracemodule.h14-45 userinterface/map/tracemodule.cpp7-36

While primarily a sensor component, the `UbloxBasestation`

interacts with the map context by providing the ENU reference point and RTCM corrections.

`rtcmData`

signals which are typically routed to the `MavsdkVehicleServer`

for injection into the vehicle's GNSS receiver sensors/gnss/ublox_basestation.cpp32-44Sources: sensors/gnss/ublox_basestation.h18-58 sensors/gnss/ublox_basestation.cpp140-160

Refresh this wiki

This wiki was recently refreshed. Please wait 6 days to refresh again.