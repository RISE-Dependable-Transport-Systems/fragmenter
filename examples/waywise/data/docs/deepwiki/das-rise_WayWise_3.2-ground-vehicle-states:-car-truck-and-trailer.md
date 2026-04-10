# Source: https://deepwiki.com/das-rise/WayWise/3.2-ground-vehicle-states:-car-truck-and-trailer

This section details the specific implementations of ground vehicle kinematics within the WayWise library. It covers the modeling of Ackermann-steered vehicles (`CarState`

), articulated heavy vehicles (`TruckState`

), and towed units (`TrailerState`

). These classes extend the base `VehicleState`

to provide specialized geometry, curvature calculations for autopilots, and simulation capabilities.

The `CarState`

class models a standard four-wheeled vehicle using an Ackermann bicycle model. It serves as the base for most ground-based vehicles in the system.

`CarState`

defines the physical footprint and axle configuration required for both path planning and rendering. Key parameters include:

`CarState`

initializes offsets for the rear axle relative to the vehicle's rear end and center vehicles/carstate.cpp18-23`CarState`

provides the conversion between the abstract "steering curvature" (used by the autopilot) and the normalized steering command (typically -1.0 to 1.0) sent to hardware vehicles/carstate.h33

`axisDistance / -steering`

vehicles/carstate.h47`CarState`

exposes its configuration to the `ParameterServer`

, allowing real-time tuning of physical dimensions and limits vehicles/carstate.cpp34

**Sources:** vehicles/carstate.h1-69 vehicles/carstate.cpp1-182

`TruckState`

extends `CarState`

to support articulated vehicles (trucks with trailers). It manages the kinematic relationship between the towing unit and the `TrailerState`

.

`TruckState`

handles the hitch geometry and the relative angle of the trailer.

`mSimulateTrailer`

is enabled, the class estimates the trailer's yaw based on the truck's movement and the physical constraints of the hitch vehicles/truckstate.cpp68-71`updateTrailingVehicleOdomPositionAndYaw`

, which calculates the new position of the trailer's rear axle based on the hitch's path vehicles/truckstate.cpp58-82A critical feature of `TruckState`

is the `getCurvatureWithTrailer`

function. This overrides the standard Ackermann curvature to allow the autopilot to steer the truck in a way that guides the *trailer* to a target point vehicles/truckstate.cpp84-107

`mPurePursuitForwardGain`

to align the trailer with the target vehicles/truckstate.cpp92-95`mPurePursuitReverseGain`

and complex geometry to calculate the "jackknife" steering required to push a trailer toward a target vehicles/truckstate.cpp96-104**Sources:** vehicles/truckstate.h1-60 vehicles/truckstate.cpp1-140

`TrailerState`

represents the passive unit in an articulated pair. It inherits from `VehicleState`

but is primarily driven by the `TruckState`

.

`updateOdomPositionAndYaw`

function is explicitly ignored because the trailer's state is updated by the towing vehicle vehicles/trailerstate.cpp54-60`RearAxleToHitchOffset`

which represents the drawbar length vehicles/trailerstate.cpp26`TRLR_WHLBASE`

, `TRLR_LENGTH`

, and `TRLR_WIDTH`

to the `ParameterServer`

vehicles/trailerstate.cpp31-35**Sources:** vehicles/trailerstate.h1-55 vehicles/trailerstate.cpp1-52

The following diagrams illustrate how the vehicle states are structured and how data flows from parameters to kinematic calculations.

This diagram maps the C++ class hierarchy to the logical vehicle types.

| Class Name | Responsibility | Primary Data Entities |
|---|---|---|
`CarState` | Ackermann steering & braking | `mAxisDistance` , `mMaxSteeringAngle` |
`TruckState` | Articulated kinematics | `mTrailerAngle_deg` , `mSimulateTrailer` |
`TrailerState` | Passive towed unit | `mWheelBase` , `mRearAxleToHitchOffset` |

**Sources:** vehicles/carstate.h20 vehicles/truckstate.h13 vehicles/trailerstate.h19

This diagram shows how the `TruckState`

uses its own state and the `TrailerState`

to provide steering commands to the autopilot.

Title: Truck and Trailer Curvature Calculation Flow

**Sources:** vehicles/truckstate.cpp26-32 vehicles/truckstate.cpp84-107

This diagram bridges the `ParameterServer`

keys to the internal member variables of the vehicle states.

Title: Parameter Server to Code Entity Mapping

**Sources:** vehicles/truckstate.cpp130-134 vehicles/trailerstate.cpp32-34

When `QT_GUI_LIB`

is defined, each state provides a `draw()`

method to render the vehicle on the `MapWidget`

.

`getAutopilotRadius()`

vehicles/carstate.cpp76-134**Sources:** vehicles/carstate.cpp32-172 vehicles/truckstate.cpp142-200 vehicles/trailerstate.cpp64-128

Refresh this wiki

This wiki was recently refreshed. Please wait 7 days to refresh again.