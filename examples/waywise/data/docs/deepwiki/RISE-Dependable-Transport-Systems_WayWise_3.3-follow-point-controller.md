# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/3.3-follow-point-controller

The Follow Point Controller enables vehicles to dynamically track a moving target point in real-time. This system is designed for "follow me" scenarios where a vehicle continuously follows a person, another vehicle, or any moving entity that provides continuous position updates.

This controller differs from waypoint following systems (see Pure Pursuit Waypoint Follower) in that it tracks a single, continuously-updated dynamic target rather than navigating through a pre-defined route. For static waypoint navigation, see Waypoint Follower Interface.

The `FollowPoint`

class supports both ground vehicles and aerial vehicles through dual operational modes:

`MovementController`

access`VehicleConnection`

commandsThe controller operates in two coordinate frame modes:

Sources: autopilot/followpoint.h1-98 autopilot/followpoint.cpp1-229

**Dual-Mode Control Architecture**

The `FollowPoint`

class provides two constructors that determine the operational mode:

| Constructor | Mode | Update Rate | Timeout | Use Case |
|---|---|---|---|---|
`FollowPoint(QSharedPointer<MovementController>)` | Local/On-Vehicle | 50ms (20Hz) | 1000ms | High-frequency control with direct actuator access |
`FollowPoint(QSharedPointer<VehicleConnection>, PosType)` | Remote/Off-Vehicle | 1000ms (1Hz) | 3000ms | Network-based control via MAVLink |

The mode is determined by the `isOnVehicle()`

method autopilot/followpoint.h47 which returns true if `mMovementController`

is non-null.

Sources: autopilot/followpoint.h43-47 autopilot/followpoint.cpp11-30

**Follow Point State Machine**

The `FollowPointSTMstates`

enum autopilot/followpoint.h20 defines three states:

| State | Description | Control Action |
|---|---|---|
`NONE` | Inactive state | No control output |
`FOLLOWING` | Actively tracking target | Steering/velocity commands to approach target |
`WAITING` | Within target radius | Hold position (zero steering/velocity) |

The state machine logic is implemented in `updateState()`

autopilot/followpoint.cpp135-168:

`distanceToPointIn2D < currentPointToFollow.getRadius()`

autopilot/followpoint.cpp150-151`distanceToPointIn2D > currentPointToFollow.getRadius()`

autopilot/followpoint.cpp164-165Sources: autopilot/followpoint.h20-35 autopilot/followpoint.cpp135-168

The FollowPoint controller supports two methods for updating the target point, corresponding to different coordinate reference frames:

**Vehicle Frame Target Calculation**

In vehicle frame mode, the target point is specified relative to the vehicle's current position and orientation (vehicle at origin). The method `updatePointToFollowInVehicleFrame()`

autopilot/followpoint.cpp94-105:

`mCurrentState.lineFromVehicleToPoint.length()`

autopilot/followpoint.cpp101This mode is independent of absolute positioning systems and works with relative odometry or visual tracking.

**ENU Frame Target Calculation**

In ENU frame mode, the target point is specified in absolute East-North-Up coordinates. The method `updatePointToFollowInEnuFrame()`

autopilot/followpoint.cpp107-117:

`distance * cos((yaw + angle) * π / 180)`

autopilot/followpoint.cpp113`distance * sin((yaw + angle) * π / 180)`

autopilot/followpoint.cpp113`point.getHeight() + followPointHeight`

autopilot/followpoint.cpp112`VehicleState::getDistanceTo()`

autopilot/followpoint.cpp115**Default Configuration:**

`followPointAngleInDeg = 180°`

places the vehicle directly behind the target`followPointDistance = 2.0m`

maintains 2 meters separation`followPointHeight = 3.0m`

maintains 3 meters altitude offset (aerial vehicles)Sources: autopilot/followpoint.cpp94-117

**Heartbeat Safety Mechanism**

The FollowPoint controller implements multiple safety mechanisms to prevent unintended vehicle behavior:

The `mFollowPointHeartbeatTimer`

autopilot/followpoint.h81 ensures continuous updates:

The controller verifies target distance every control cycle autopilot/followpoint.cpp144-149:

Default maximum distance: 100 meters autopilot/followpoint.h28

The method `thePointIsNewResetTheTimer()`

autopilot/followpoint.cpp119-133 ensures only newer points are accepted:

On stop, the controller emits `activateEmergencyBrake()`

signal autopilot/followpoint.cpp81 and on start emits `deactivateEmergencyBrake()`

autopilot/followpoint.cpp67 This integrates with vehicle-level safety systems.

Sources: autopilot/followpoint.h69-81 autopilot/followpoint.cpp44-92 autopilot/followpoint.cpp119-148

**Control Loop State Machine Logic**

For ground vehicles, the controller calculates steering curvature autopilot/followpoint.cpp154:

The method `getCurvatureToPointInVehicleFrame()`

uses the bicycle kinematic model to compute appropriate steering.

For MAVLink-based control, the controller sends position setpoints autopilot/followpoint.cpp157:

The boolean parameter `true`

indicates continuous setpoint mode (position hold mode).

When WAITING or stopping, the controller executes `holdPosition()`

autopilot/followpoint.cpp84-92:

Sources: autopilot/followpoint.cpp135-168 autopilot/followpoint.cpp84-92

The FollowPoint controller exposes parameters through the `ParameterServer`

for runtime configuration:

| Parameter ID | Type | Default | Description | Applies To |
|---|---|---|---|---|
`FP{id}_DIST` | float | 2.0 | Follow point distance (meters) | All vehicles |
`FP{id}_MAX_DIST` | float | 100 | Maximum tracking distance (meters) | All vehicles |
`FP{id}_HEIGHT` | float | 3.0 | Follow point height offset (meters) | Aerial vehicles |
`FP{id}_ANGLE_DEG` | float | 180 | Follow point angle (degrees, -180 to 180) | Aerial vehicles |

Where `{id}`

is the vehicle ID from `VehicleState::getId()`

.

The method `provideParametersToParameterServer()`

autopilot/followpoint.cpp32-42 registers parameters using getter/setter function bindings:

This allows parameters to be:

**Ground Vehicles:**

`followPointSpeed`

autopilot/followpoint.h30: Desired speed while following (m/s)`autopilotRadius`

autopilot/followpoint.h31: Radius for intersection calculation (meters)**Aerial Vehicles:**

`followPointHeight`

autopilot/followpoint.h33: Height offset above/below target (meters)`followPointAngleInDeg`

autopilot/followpoint.h34: Angular offset around target (-180° to 180°)Sources: autopilot/followpoint.h22-35 autopilot/followpoint.cpp32-42 autopilot/followpoint.cpp170-228

**System Integration Architecture**

`startFollowPoint()`

autopilot/followpoint.cpp65-72`stopFollowPoint()`

autopilot/followpoint.cpp74-82The `mPosTypeUsed`

member autopilot/followpoint.h84 specifies which position estimate to use:

`PosType::fused`

: GNSS + IMU fused estimate (default)`PosType::GNSS`

: Raw GNSS position`PosType::odom`

: Odometry-based positionThis is set during remote-mode construction autopilot/followpoint.cpp22 and used when reading vehicle position autopilot/followpoint.cpp90 autopilot/followpoint.cpp115

Sources: autopilot/followpoint.h84-90 autopilot/followpoint.cpp11-30 autopilot/followpoint.cpp65-92

While FollowPoint is a standalone controller, it can coexist with waypoint following systems. The `MultiWaypointFollower`

class autopilot/multiwaypointfollower.h manages multiple `WaypointFollower`

instances (see Multi-Waypoint Follower), allowing systems to switch between:

However, FollowPoint does not inherit from `WaypointFollower`

and operates independently. Applications must manage exclusive control - only one autopilot mode should be active at a time.

Sources: autopilot/multiwaypointfollower.h1-65 autopilot/multiwaypointfollower.cpp1-161

| Timer | Purpose | Period | Type |
|---|---|---|---|
`mUpdateStateTimer` | Control loop execution | 50ms (local) / 1000ms (remote) | Repeating |
`mFollowPointHeartbeatTimer` | Timeout detection | 1000ms (local) / 3000ms (remote) | Single-shot, reset on update |

Declared at autopilot/followpoint.h78-82 initialized at autopilot/followpoint.cpp44-58

The `FollowPointState`

struct autopilot/followpoint.h22-35 encapsulates all controller state:

`stmState`

)`currentPointToFollow`

)`distanceToPointIn2D`

)`lineFromVehicleToPoint`

)The controller relies on:

`VehicleState::getCurvatureToPointInVehicleFrame()`

: Converts vehicle-frame point to steering curvature`VehicleState::getPosition()`

: Retrieves vehicle position in specified frame`VehicleState::getDistanceTo()`

: Calculates Euclidean distance between points`geometry::findIntersectionsBetweenCircleAndLine()`

: Computes autopilot radius intersection autopilot/followpoint.cpp102Sources: autopilot/followpoint.h1-98 autopilot/followpoint.cpp1-229

Refresh this wiki
