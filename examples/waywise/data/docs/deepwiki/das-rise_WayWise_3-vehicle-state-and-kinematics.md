# Source: https://deepwiki.com/das-rise/WayWise/3-vehicle-state-and-kinematics

The **Vehicle State & Kinematics** module provides a structured hierarchy for representing physical objects and vehicles within the WayWise ecosystem. It abstracts the complexities of multi-source positioning, physical dimensions, and movement constraints, allowing the autopilot and UI layers to interact with diverse hardware (cars, trucks, copters) through a unified interface.

WayWise employs an inheritance-based model to manage state. At the root is `ObjectState`

, which handles generic spatial data. `VehicleState`

extends this with autopilot-specific properties and movement constraints. Specific vehicle types then implement their unique kinematic models (e.g., Ackermann for cars or differential drive).

The following diagram maps the conceptual vehicle types to their corresponding C++ classes and the `WAYWISE_OBJECT_TYPE`

enum.

**Sources:** vehicles/objectstate.h22-31 vehicles/vehiclestate.h25-131

`ObjectState`

is the base class for any entity that exists in a 3D coordinate system. Its primary role is managing the **ENU (East-North-Up)** reference point and maintaining an array of positions from different sources (GNSS, IMU, Odometry, Fused, etc.).

| Feature | Implementation |
|---|---|
Multi-Source Position | Stores positions in `mPositionBySource` indexed by `PosType` vehicles/objectstate.h96 |
Coordinate Reference | Manages a global `llh_t` (Latitude, Longitude, Height) reference to anchor local ENU coordinates vehicles/objectstate.cpp60-65 |
Signals | Emits `positionUpdated(PosType)` and `updatedEnuReference(llh_t)` to notify the UI and controllers vehicles/objectstate.h75-78 |

For details, see ObjectState & VehicleState Base Classes.

`VehicleState`

introduces vehicle-specific dynamics. It tracks the current `FlightMode`

(compatible with MAVSDK), steering values normalized from -1.0 to 1.0, and provides helper functions for **Pure Pursuit** navigation.

`getCurvatureToPointInVehicleFrame`

calculates the required curvature to reach a target point based on the vehicle's current orientation vehicles/vehiclestate.cpp93-100For details, see ObjectState & VehicleState Base Classes.

Ground vehicles implement specific steering geometry. `CarState`

typically handles Ackermann steering, while `TruckState`

manages the complexities of articulated units.

`VehicleState`

supports a "trailing vehicle" link via `mTrailingVehicle`

, allowing a truck to possess a `TrailerState`

vehicles/vehiclestate.cpp109-117`steeringCurvatureToSteering()`

to map geometric curvature to hardware-specific actuator commands vehicles/vehiclestate.h97For details, see Ground Vehicle States: Car, Truck & Trailer.

`VehicleLighting`

.For details, see Copter & Differential-Drive Vehicle States.

The following diagram illustrates how the `ObjectState`

hierarchy bridges internal data structures to the visual representation in the `MapWidget`

.

**Sources:** vehicles/objectstate.cpp38-43 vehicles/vehiclestate.h51-54 vehicles/objectstate.h40-43

**Sources:**

Refresh this wiki

This wiki was recently refreshed. Please wait 7 days to refresh again.