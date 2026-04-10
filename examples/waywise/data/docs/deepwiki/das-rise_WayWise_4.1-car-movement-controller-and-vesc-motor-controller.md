# Source: https://deepwiki.com/das-rise/WayWise/4.1-car-movement-controller-and-vesc-motor-controller

This section details the movement control architecture for Ackermann-steered vehicles within WayWise. The system bridges high-level autopilot commands (speed and steering) to physical actuators using a hierarchical controller approach.

The `CarMovementController`

is the primary implementation of the `MovementController`

interface for car-like vehicles vehicles/controller/carmovementcontroller.h19-20 It translates desired speed (m/s) and steering normalized units ([-1.0, 1.0]) into motor RPM and servo positions vehicles/controller/carmovementcontroller.cpp28-35

`CarState`

directly (as feedback from servos is typically unavailable) and forwards the command to a `ServoController`

vehicles/controller/carmovementcontroller.cpp14-26`mSpeedToRPMFactor`

), which defaults to 4123.3 (calibrated for a Traxxas Slash VXL) vehicles/controller/carmovementcontroller.h45 The calculated RPM is then sent to the `MotorController`

vehicles/controller/carmovementcontroller.cpp33The controller listens for feedback from the motor controller (e.g., tachometer pulses). When `gotStatusValues`

is emitted, it calculates the driven distance and updates the vehicle's odometry vehicles/controller/carmovementcontroller.cpp58-77

In simulation, the controller bypasses hardware and calculates movement based on the elapsed time (`dt_ms`

) and desired speed, manually updating the `CarState`

position and yaw vehicles/controller/carmovementcontroller.cpp79-88

**Movement Control Data Flow**

Sources: vehicles/controller/carmovementcontroller.cpp5-103 vehicles/controller/movementcontroller.h17-46

The `VESCMotorController`

implements the `MotorController`

interface specifically for hardware using the VESC (Vedder Electronic Speed Controller) open-source project protocol vehicles/controller/vescmotorcontroller.h23-24

The controller communicates via `QSerialPort`

at 115200 baud vehicles/controller/vescmotorcontroller.cpp79 It utilizes `VESC::Packet`

to wrap and unwrap binary payloads vehicles/controller/vescmotorcontroller.cpp16-26

Key periodic tasks:

`COMM_ALIVE`

every 300ms to prevent VESC safety timeouts vehicles/controller/vescmotorcontroller.cpp29-34`COMM_GET_VALUES_SELECTIVE`

vehicles/controller/vescmotorcontroller.cpp36-41When a packet is received, `processVESCPacket`

decodes the binary data into the `VESC::MC_VALUES`

struct. It extracts:

`rpm`

: The current motor RPM vehicles/controller/vescmotorcontroller.cpp210`tachometer`

: Total pulses for distance calculation vehicles/controller/vescmotorcontroller.cpp215`temp_mos`

& `v_in`

: Hardware health monitoring vehicles/controller/vescmotorcontroller.cpp207-212**VESC Protocol Entity Mapping**

Sources: vehicles/controller/vescmotorcontroller.cpp11-64 vehicles/controller/vescmotorcontroller.h71-109

The VESC hardware often serves as a multi-purpose hub, providing PWM output for servos and integrated IMU data.

The `ServoController`

is an abstract class providing range and center calibration vehicles/controller/servocontroller.h13-37

`VESCMotorController`

that implements `requestServoPosition`

by sending the `COMM_SET_SERVO_POS`

packet vehicles/controller/vescmotorcontroller.cpp124-130`setInvertOutput`

, `setServoRange`

, and `setServoCenter`

to map normalized [-1.0, 1.0] inputs to hardware-specific PWM widths vehicles/controller/servocontroller.cpp37-45WayWise provides multiple ways to update vehicle orientation:

`COMM_GET_IMU_DATA`

vehicles/controller/vescmotorcontroller.h53-69`/dev/i2c-1`

) sensors/imu/bno055orientationupdater.h18-30 It polls the sensor periodically and updates the `ObjectState`

with ENU-converted yaw sensors/imu/bno055orientationupdater.cpp22-38| Class | Interface | Primary Role |
|---|---|---|
`CarMovementController` | `MovementController` | High-level Ackermann logic and speed-to-RPM conversion. |
`VESCMotorController` | `MotorController` | Serial communication with VESC hardware. |
`VESCServoController` | `ServoController` | PWM steering control via VESC. |
`BNO055OrientationUpdater` | `IMUOrientationUpdater` | Independent I2C IMU polling. |

Sources: vehicles/controller/servocontroller.cpp5-46 vehicles/controller/vescmotorcontroller.cpp137-143 sensors/imu/bno055orientationupdater.cpp8-42

Refresh this wiki

This wiki was recently refreshed. Please wait 7 days to refresh again.