# Source: https://deepwiki.com/das-rise/WayWise/3.3-copter-and-differential-drive-vehicle-states

This section details the specialized vehicle state implementations for multicopters and differential-drive platforms. While both inherit from the base `VehicleState`

class, they implement unique kinematic models, operational states (such as flight modes and landed states), and hardware-level integrations like GPIO-controlled lighting.

`CopterState`

is the specialized implementation for multicopter UAVs (Unmanned Aerial Vehicles). It extends the standard vehicle state with drone-specific parameters such as frame configuration, propeller dimensions, and altitude-dependent states vehicles/copterstate.h16-17

The class supports different frame types (X or PLUS) and handles the rendering of the drone on the `MapWidget`

vehicles/copterstate.h20-23 The drawing logic includes:

`CopterState`

tracks the vertical operational status of the vehicle via the `LandedState`

enum vehicles/copterstate.h26-32

| State | Description |
|---|---|
`OnGround` | Vehicle is landed and stationary. |
`TakingOff` | Transitioning from ground to air. |
`InAir` | Active flight. |
`Landing` | Descending to touch down. |
`Unknown` | Initial state or loss of telemetry. |

The class also maps `FlightMode`

(inherited from `VehicleState`

) to human-readable strings for UI display, covering modes like `Takeoff`

, `ReturnToLaunch`

, `Offboard`

, and `FollowMe`

vehicles/copterstate.cpp143-160

**Sources:** vehicles/copterstate.h1-50 vehicles/copterstate.cpp1-170

`DiffDriveVehicleState`

implements the kinematics for differential-drive robots (e.g., skid-steer or two-wheeled robots). Unlike Ackermann vehicles, these platforms change heading by varying the relative speeds of the left and right drive actuators vehicles/diffdrivevehiclestate.h13-14

The class overrides the standard steering and speed setters to manage individual wheel speeds vehicles/diffdrivevehiclestate.h18-20:

`mSpeedLeft`

/ `mSpeedRight`

`steeringCurvatureToSteering`

`updateOdomPositionAndYaw`

to calculate displacement and rotation based on the average and difference of the driven distances of both sides vehicles/diffdrivevehiclestate.h22The following diagram shows how high-level movement commands are translated into the internal state of a differential vehicle.

**Differential Drive State Mapping**

**Sources:** vehicles/diffdrivevehiclestate.h1-38 autopilot/waypointfollower.h14-38

The `VehicleLighting`

class provides a hardware abstraction for physical status indicators using GPIO (via `libgpiod`

). It automatically updates lighting states based on the current telemetry of a `VehicleState`

object vehicles/vehiclelighting.h20-22

The class runs an internal `QTimer`

(defaulting to 500ms) that polls the associated `VehicleState`

vehicles/vehiclelighting.cpp32-33:

The implementation targets specific GPIO lines, typically on a Linux-based SBC like a Raspberry Pi vehicles/vehiclelighting.cpp21-30:

| Function | GPIO Line (Default) | LED Color |
|---|---|---|
`mBackupLight` | 22 | White |
`mBrakeLight` | 23 | Red |
`mRightTurnSignal` | 24 | Orange |
`mLeftTurnSignal` | 25 | Orange |

**Sources:** vehicles/vehiclelighting.h1-49 vehicles/vehiclelighting.cpp1-114

The `EmergencyBrake`

class acts as a safety supervisor that can override vehicle movement based on sensor inputs autopilot/emergencybrake.h23-24

The system fuses different inputs to trigger an `emergencyBrake()`

signal autopilot/emergencybrake.cpp36-43:

`brakeForDetectedCameraObject()`

slot receives `PosPoint`

data (e.g., from a DepthAI camera). It calculates the Euclidean distance and triggers a brake if the object is within the `brakeForObjectAtDistance`

threshold (default 10m) autopilot/emergencybrake.cpp23-34`WaypointFollower`

implementations can signal `activateEmergencyBrake()`

to the class autopilot/waypointfollower.h37 autopilot/emergencybrake.cpp18-21**Safety Data Flow**

**Sources:** autopilot/emergencybrake.h1-43 autopilot/emergencybrake.cpp1-44 autopilot/waypointfollower.h35-38

Refresh this wiki

This wiki was recently refreshed. Please wait 7 days to refresh again.