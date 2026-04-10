# Source: https://deepwiki.com/das-rise/WayWise/7.3-imu-angle-uwb-and-tof-sensors

This page details the sensor integration layer for inertial measurement units (IMU), magnetic angle sensors, Ultra-Wideband (UWB) positioning, and Time-of-Flight (ToF) distance sensors. These sensors provide critical feedback for vehicle orientation, articulated trailer angles, and local obstacle detection.

The codebase uses a hierarchical approach for IMU data, where an abstract `IMUOrientationUpdater`

manages the association between a sensor and an `ObjectState`

.

The system supports multiple IMU sources. Data is typically polled or received via serial/I2C, converted to the ENU (East-North-Up) coordinate system, and stored in the `ObjectState`

under the `PosType::IMU`

slot.

| Class | Description | Implementation Detail |
|---|---|---|
`IMUOrientationUpdater` | Abstract base class. | Defines `updatedIMUOrientation` signal and simulation logic sensors/imu/imuorientationupdater.h15-26 |
`BNO055OrientationUpdater` | Driver for Bosch BNO055. | Uses I2C polling and the `pi-bno055` external library sensors/imu/bno055orientationupdater.cpp10-24 |
`VESCOrientationUpdater` | VESC-integrated IMU. | Nested class within `VESCMotorController` that extracts IMU data from VESC telemetry vehicles/controller/vescmotorcontroller.h53-69 |

The `BNO055OrientationUpdater`

initializes the sensor in `imu`

mode (Euler angles without magnetometer) sensors/imu/bno055orientationupdater.cpp18-20 It polls the sensor at a default interval of 20ms sensors/imu/bno055orientationupdater.h28

`coordinateTransforms::yawNEDtoENU`

sensors/imu/bno055orientationupdater.cpp32`PosPoint`

and written to the `ObjectState`

sensors/imu/bno055orientationupdater.cpp30-34When using a VESC motor controller, the IMU data can be requested via the `COMM_GET_IMU_DATA`

packet vehicles/controller/vescmotorcontroller.cpp44-46 The `VESCOrientationUpdater`

handles the incoming stream and updates the `ObjectState`

similarly to the standalone drivers vehicles/controller/vescmotorcontroller.h57-66

The base class provides a `simulationStep`

function that estimates IMU movement based on odometry (`PosType::odom`

) when hardware is not present sensors/imu/imuorientationupdater.cpp17-46

**Sensor to State Mapping**

Sources: sensors/imu/imuorientationupdater.h15-30 sensors/imu/bno055orientationupdater.cpp22-38 vehicles/controller/vescmotorcontroller.h53-69

The `AS5600Updater`

is specifically used to measure the articulation angle between a truck and its trailer. It interfaces with the AS5600 12-bit magnetic rotary position sensor via I2C sensors/angle/as5600updater.h19-21

`as5600_basic_init()`

to prepare the I2C bus (default address 0x36) sensors/angle/as5600updater.cpp12-13`QTimer`

triggers `as5600_basic_read()`

every 50ms sensors/angle/as5600updater.cpp22-37`VehicleState`

to a `TruckState`

to call `setTrailerAngle()`

sensors/angle/as5600updater.cpp27-29`angleOffset`

to normalize the zero-point of the physical magnetic mount sensors/angle/as5600updater.cpp25**Trailer Angle Data Flow**

Sources: sensors/angle/as5600updater.cpp9-41 sensors/angle/as5600updater.h20-34 external/pi-as5600/readme.md22-23

The `VL53L0XToFSensor`

provides short-range distance measurements, typically used for obstacle detection or precision docking.

`VL53L0X`

library to communicate over I2C (default address 0x29) sensors/tof/vl53l0xtofsensor.cpp15`updatedDistance(double distance_m)`

upon every successful poll sensors/tof/vl53l0xtofsensor.cpp31Sources: sensors/tof/vl53l0xtofsensor.cpp13-35 sensors/tof/tofsensor.h13-26

The `PozyxPositionUpdater`

provides local positioning data using Ultra-Wideband anchors.

`ObjectState`

with `PosType::UWB`

. This is often used as a fallback or augmentation for GNSS in indoor or obstructed environments.Sources: sensors/uwb/pozyxpositionupdater.h10-25 sensors/uwb/pozyxpositionupdater.cpp5-15 (referenced from file list).

| Sensor Type | Implementation Class | Interface | Update Rate |
|---|---|---|---|
IMU | `BNO055OrientationUpdater` | I2C (`/dev/i2c-1` ) | 50 Hz (20ms) |
IMU | `VESCOrientationUpdater` | Serial (via VESC) | 50 Hz (20ms) |
Angle | `AS5600Updater` | I2C (0x36) | 20 Hz (50ms) |
ToF | `VL53L0XToFSensor` | I2C (0x29) | 20 Hz (50ms) |
UWB | `PozyxPositionUpdater` | Serial | Variable |

Sources: sensors/imu/bno055orientationupdater.h28 sensors/angle/as5600updater.h29 sensors/tof/vl53l0xtofsensor.cpp33 vehicles/controller/vescmotorcontroller.h92

Refresh this wiki

This wiki was recently refreshed. Please wait 6 days to refresh again.