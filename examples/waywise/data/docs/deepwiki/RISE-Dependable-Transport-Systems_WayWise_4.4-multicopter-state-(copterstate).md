# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/4.4-multicopter-state-(copterstate)

This page documents `CopterState`

, the vehicle state implementation for multicopter drones and UAVs in WayWise. `CopterState`

extends the base `VehicleState`

class to provide multicopter-specific properties including frame configuration, landed state tracking, and drone-specific kinematics. This class is used by flight control systems, visualization components, and autopilot algorithms when operating multicopter vehicles.

For the base vehicle state architecture and position tracking system, see Vehicle State Architecture & Position Sources. For ground vehicle implementations, see Ground Vehicle Models (CarState). For flight control UI that operates on `CopterState`

, see Drone Flight Control UI.

`CopterState`

inherits from `VehicleState`

, which in turn inherits from `ObjectState`

. This hierarchy provides multicopters with the same multi-source position tracking (`mPositionBySource`

array), flight mode management, and coordinate system support as other vehicles, while adding drone-specific functionality.

**Sources:** vehicles/copterstate.h1-50 vehicles/copterstate.cpp1-224

The constructor at vehicles/copterstate.cpp12-21 initializes default values based on the Holybro S500/X500 platform and sets the Waywise object type to `WAYWISE_OBJECT_TYPE_QUADCOPTER`

.

Multicopters can be configured in two frame arrangements, defined by the `CopterFrameType`

enumeration:

| Frame Type | Description | Motor Arrangement | Visual Rotation Offset |
|---|---|---|---|
`X` | X-frame configuration | Motors positioned at 45° angles | +45° rotation applied in visualization |
`PLUS` | Plus-frame configuration | Motors aligned with forward/lateral axes | No rotation offset |

**Sources:** vehicles/copterstate.h20-23 vehicles/copterstate.cpp101

The frame type affects visualization rendering at vehicles/copterstate.cpp101 where an X-frame receives a 45° rotation offset, and propeller color coding at vehicles/copterstate.cpp109-117 where the PLUS configuration uses different colors for front vs. side propellers.

`CopterState`

tracks the drone's landing status through the `LandedState`

enumeration, which mirrors the MAVSDK LandedState definition. This state is independent of the `FlightMode`

(inherited from `VehicleState`

) and provides finer-grained information about ground contact and transitions.

| Landed State | Description | Typical Flight Mode |
|---|---|---|
`Unknown` | Landed state not determined | `Unknown` |
`OnGround` | Vehicle is on the ground, rotors may be spinning | `Hold` , `Ready` |
`InAir` | Vehicle is airborne | `Hold` , `Mission` , `Offboard` |
`TakingOff` | Transition from ground to air | `Takeoff` |
`Landing` | Transition from air to ground | `Land` |

**Sources:** vehicles/copterstate.h26-32 vehicles/copterstate.cpp134-140 vehicles/copterstate.cpp215-223

The landed state is accessed via `getLandedState()`

and `setLandedState()`

methods at vehicles/copterstate.cpp215-223 The state is displayed in the vehicle's text overlay during visualization at vehicles/copterstate.cpp133-140

The `draw()`

method at vehicles/copterstate.cpp23-192 renders the multicopter on the map with several visual elements:

**Sources:** vehicles/copterstate.cpp23-192

The visualization adapts based on the zoom level:

| Scale Threshold | Rendering Mode | Elements Displayed |
|---|---|---|
`scale < 0.05` | Simplified | Arrow shape with vehicle color |
`scale >= 0.05` | Detailed | Frame arms, propellers, velocity vector |

**Sources:** vehicles/copterstate.cpp33-37 vehicles/copterstate.cpp87-126

The home position (used for Return-To-Launch) is rendered at vehicles/copterstate.cpp42-58 as:

For detailed rendering, propellers are color-coded to indicate orientation when the vehicle is selected:

When not selected, all propellers are gray.

**Sources:** vehicles/copterstate.cpp74-84 vehicles/copterstate.cpp109-117

The text overlay at vehicles/copterstate.cpp129-175 displays:

`(x, y, height, yaw)`

**Sources:** vehicles/copterstate.cpp161-175

The `updateOdomPositionAndYaw()`

method at vehicles/copterstate.cpp194-207 implements 3D dead reckoning for multicopters. Unlike ground vehicles that update only in the XY plane, this method updates all three spatial dimensions.

**Algorithm:**

`PosType`

source`sqrt(vx² + vy² + vz²)`

`position = position + drivenDistance * normalizedVelocity`

**Sources:** vehicles/copterstate.cpp194-207

**Key Difference from Ground Vehicles:** While `CarState::updateOdomPositionAndYaw()`

uses bicycle kinematics with steering angles, `CopterState`

performs simple 3D linear interpolation based on velocity direction. The multicopter is assumed to move in the direction of its velocity vector.

The `steeringCurvatureToSteering()`

method at vehicles/copterstate.cpp209-213 converts a desired curvature into differential thrust commands. The implementation treats the multicopter similar to a differential-drive robot in the XY plane:

```
steering = (width / 2) * curvature
```


Where:

`width`

is the distance between left and right propeller centers (e.g., 520mm for S500)`curvature`

is the inverse of the turn radius (1/m)`steering`

represents the differential wheel speed for equivalent differential drive**Sources:** vehicles/copterstate.cpp209-213

This simplified model allows multicopters to use the same autopilot interfaces as ground vehicles. The actual motor mixing and attitude control are handled by the flight controller firmware (e.g., PX4).

`CopterState`

integrates with the autopilot layer through the `WaypointFollower`

interface. While ground vehicles typically use `PurepursuitWaypointFollower`

for path tracking, multicopters often use simpler waypoint-to-waypoint navigation through `GotoWaypointFollower`

or dynamic point following via `FollowPoint`

.

**Sources:** autopilot/waypointfollower.h1-41 autopilot/emergencybrake.h1-43

The flight mode stored in `CopterState`

(inherited from `VehicleState`

) determines which autopilot system is active:

| Flight Mode | Autopilot Component | Typical Use Case |
|---|---|---|
`Mission` | `GotoWaypointFollower` or `MultiWaypointFollower` | Pre-planned waypoint sequence |
`Offboard` | `FollowPoint` | Dynamic target following |
`Hold` | None (direct control) | Position hold commanded by flight controller |
`Manual` , `Posctl` , `Altctl` | None | Manual pilot control with varying autonomy levels |

The `EmergencyBrake`

system at autopilot/emergencybrake.h1-43 can interrupt any autopilot mode when obstacles are detected. Waypoint followers emit `activateEmergencyBrake()`

and `deactivateEmergencyBrake()`

signals at autopilot/waypointfollower.h36-37 to control the safety system.

For multicopters, the `EmergencyBrakeState`

at autopilot/emergencybrake.h15-21 includes:

`brakeForDetectedCameraObject`

: Trigger based on camera vision`brakeForDetectedLidarObject`

: Trigger based on lidar range`brakeForObjectAtDistance`

: Distance threshold (default: 10m)When activated, the emergency brake signal interrupts the autopilot, typically commanding a stop or hover.

**Sources:** autopilot/emergencybrake.h15-21 autopilot/emergencybrake.cpp36-43

The constructor at vehicles/copterstate.cpp12-21 initializes default parameters for the Holybro S500/X500 quadcopter:

| Parameter | Default Value | Description |
|---|---|---|
`mFrameType` | `CopterFrameType::X` | X-frame configuration |
`mPropellerSize` | 260 mm | Propeller diameter |
`mWidth` | 520 mm | Distance between left-right motor centers |
`mLength` | 520 mm | Distance between front-rear motor centers |
| Object Type | `WAYWISE_OBJECT_TYPE_QUADCOPTER` | Waywise type identifier |

These defaults provide a reasonable starting point for common quadcopter platforms. The dimensions are used for visualization scaling, collision detection, and the differential steering calculation.

**Sources:** vehicles/copterstate.cpp14-20

Refresh this wiki
