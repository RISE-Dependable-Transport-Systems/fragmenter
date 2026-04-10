# Source: https://deepwiki.com/das-rise/WayWise/4-movement-controllers

The `MovementController`

layer serves as the essential bridge between high-level autopilot commands (such as those from a `WaypointFollower`

) and the low-level hardware actuators (motors and servos). It abstracts the vehicle's kinematic model, ensuring that generic speed and steering requests are translated into hardware-specific signals like RPM or PWM pulse widths vehicles/controller/movementcontroller.h5-8

This abstraction allows the autopilot logic to remain agnostic of whether it is controlling a small RC car via a VESC motor controller or a heavy industrial vehicle via CANopen.

The base `MovementController`

class defines the standard interface for setting desired vehicle states. It maintains a reference to a `VehicleState`

object, which it updates based on feedback from the hardware vehicles/controller/movementcontroller.h21-31

**Key Responsibilities:**

`updatedOdomPositionAndYaw`

when the vehicle moves, allowing for dead-reckoning vehicles/controller/movementcontroller.h39`actuateDriveMotor()`

and `actuateSteeringServo()`

to be implemented by hardware-specific subclasses vehicles/controller/movementcontroller.h33-34`simulationStep()`

for testing logic without physical hardware vehicles/controller/movementcontroller.h36**Sources:** vehicles/controller/movementcontroller.h5-46 vehicles/controller/movementcontroller.cpp1-103

The following diagram illustrates how the `MovementController`

sits between the high-level state representation and the physical hardware interfaces.

**Movement Controller Architecture**

**Sources:** vehicles/controller/movementcontroller.h17-46 vehicles/controller/carmovementcontroller.h19-47 vehicles/controller/motorcontroller.h13-26

The `CarMovementController`

is the primary implementation for Ackermann-steered vehicles. It coordinates a `MotorController`

(typically a VESC) and a `ServoController`

.

`mSpeedToRPMFactor`

vehicles/controller/carmovementcontroller.h45-46`gotStatusValues`

from the motor controller to calculate `drivenDistance`

via tachometer pulses and update the vehicle's velocity in `CarState`

vehicles/controller/carmovementcontroller.cpp58-77`ServoController`

to map normalized steering values to hardware-specific ranges, including support for inversion and center-trimming vehicles/controller/servocontroller.cpp37-45For details on VESC protocols and PWM servo configuration, see Car Movement Controller & VESC Motor Controller.

**Sources:** vehicles/controller/carmovementcontroller.cpp5-56 vehicles/controller/servocontroller.h13-37

For industrial applications, the `CANopenMovementController`

interfaces with heavy-duty motor drives over a CAN bus.

`CANopenControllerInterface`

to manage communication with EDS-configured slaves.For details on CANopen state machines and PDO mapping, see CANopen Movement Controller.

The library uses abstract base classes for actuators to allow swapping hardware backends without changing the movement logic.

| Abstract Class | Purpose | Key Methods |
|---|---|---|
`MotorController` | Interface for drive motors | `requestRPM()` , `pollFirmwareVersion()` vehicles/controller/motorcontroller.h17-18 |
`ServoController` | Interface for steering servos | `requestSteering()` , `setServoCenter()` vehicles/controller/servocontroller.h20-26 |

**Sources:** vehicles/controller/motorcontroller.h13-26 vehicles/controller/servocontroller.h13-37

**Actuator Signal Flow**

**Sources:** vehicles/controller/carmovementcontroller.cpp28-35 vehicles/controller/carmovementcontroller.cpp58-77 vehicles/controller/servocontroller.cpp37-45

Refresh this wiki

This wiki was recently refreshed. Please wait 7 days to refresh again.