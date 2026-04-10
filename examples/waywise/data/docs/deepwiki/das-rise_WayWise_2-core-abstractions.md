# Source: https://deepwiki.com/das-rise/WayWise/2-core-abstractions

This section provides an overview of the foundational data types, coordinate systems, and utility classes that form the backbone of the WayWise library. These abstractions ensure that vehicle state, sensor data, and movement commands are handled consistently across different hardware platforms and communication protocols.

The following diagram illustrates how raw geographic data and sensor inputs are transformed into the core entities used by the autopilot and UI subsystems.

**Data Transformation Overview**

**Sources:** core/coordinatetransforms.h14-30 core/pospoint.h25-33

The `PosPoint`

class is the primary container for spatial and kinematic data within WayWise. It encapsulates 3D position, orientation (Roll, Pitch, Yaw), speed, and metadata such as timestamps and source types.

`PosType`

enum to identify the data source (e.g., GNSS, Fused, Simulated) core/pospoint.h13-22**Coordinate Frame Relationships**

**Sources:** core/coordinatetransforms.h153-192 core/pospoint.cpp279-288

For a deep dive into the math and implementation of these transforms, see PosPoint & Coordinate Transforms.

Beyond spatial data, WayWise relies on several infrastructure utilities to manage system health, binary data, and logging.

| Class | Primary Responsibility | File Pointer |
|---|---|---|
`PosPoint` | 3D State Representation | core/pospoint.h25 |
`xyz_t` | 3D Vector Math | core/coordinatetransforms.h26 |
`llh_t` | Geodetic Coordinates | core/coordinatetransforms.h14 |

For details on these infrastructure components, see Utility Classes.

**Sources:**

`PosPoint`

definition: core/pospoint.h25-106`PosType`

enumeration: core/pospoint.h13-22Refresh this wiki

This wiki was recently refreshed. Please wait 6 days to refresh again.