# Source: https://deepwiki.com/das-rise/WayWise/10.2-external-dependencies-and-libraries

WayWise relies on a set of vendored external libraries and drivers to interface with specific hardware (VESC motor controllers, I2C sensors) and to implement industry-standard communication protocols (ISO 22133). These dependencies are located primarily in the `external/`

and `ext/`

directories, or integrated as git submodules.

The ISO 22133 implementation is a critical dependency for industrial interoperability. It is integrated via a git submodule at `examples/RCCar_ISO22133_autopilot/isoObject`

.gitmodules1-4 The `iso22133VehicleServer`

class bridges this library with the WayWise `VehicleState`

and `WaypointFollower`

abstractions.

The `iso22133VehicleServer`

inherits from both `VehicleServer`

and `ISO22133::TestObject`

communication/iso22133vehicleserver.h10 It handles the conversion between ISO 22133 trajectory formats and internal `PosPoint`

structures.

**Key Functions:**

`onOSEM()`

: Handles Object Settings; sets the ENU reference for the vehicle state based on the received coordinate system origin communication/iso22133vehicleserver.cpp159-169`onTRAJ()`

: Triggered when new trajectory segments are available. It clears the current route and appends new `PosPoint`

objects converted from the ISO segments communication/iso22133vehicleserver.cpp171-193`setMonr()`

: Publishes the current vehicle state (position, speed, acceleration, drive direction) to the ISO 22133 Monitoring (MONR) message at a 10ms interval communication/iso22133vehicleserver.cpp39-80The following diagram illustrates how the external `ISO22133::TestObject`

interacts with the WayWise core entities.

**ISO 22133 Bridge Architecture**

**Sources:** communication/iso22133vehicleserver.h10-37 communication/iso22133vehicleserver.cpp171-193 communication/iso22133vehicleserver.cpp159-169

Located in `external/vesc/`

, this library provides the communication protocol for Vedder Electronic Speed Controllers (VESC). The primary interface is the `VESC::Packet`

class.

**Key Features:**

`processData()`

to ingest raw serial bytes and emits `packetReceived()`

once a full frame is validated external/vesc/vescpacket.h40-43`mRxTimer`

) to reset the packet parser if bytes are delayed external/vesc/vescpacket.h49-54**Sources:** external/vesc/vescpacket.h26-64

WayWise vendors several drivers for low-level sensor interaction, specifically optimized for the Raspberry Pi.

The `external/pi-as5600/`

directory contains a C port driver for the AS5600 12-bit magnetic rotary encoder, used primarily for measuring trailer articulation angles.

`0x36`

) external/pi-as5600/readme.md22`ZPOS`

(Start Position) and `MPOS`

(Stop Position) for scaling the output angle external/pi-as5600/readme.md48-62`AS5600AngleSensorUpdater`

to provide real-time hitch angle data.The `external/VL53L0X/`

library is a simplified C port of the Pololu Arduino library for Linux external/VL53L0X/README.md3-13

`tofInit()`

: Initializes the I2C bus and sensor "magic numbers" external/VL53L0X/tof.c97-118`tofReadDistance()`

: Returns the current distance in millimeters external/VL53L0X/tof.h30`ioctl`

calls to `/dev/i2c-x`

external/VL53L0X/tof.c101-114`ext/Fusion`

(or `external/Fusion`

), this is a high-performance 9-axis sensor fusion library. It takes accelerometer, gyroscope, and magnetometer data to produce stable Euler angles and quaternions, used when the BNO055 is not in "NDOF" (on-chip fusion) mode.**Sources:** external/pi-as5600/readme.md1-73 external/VL53L0X/README.md1-20 external/VL53L0X/tof.c97-118 external/VL53L0X/tof.h1-38

This diagram maps the external software libraries to the physical hardware components and the internal WayWise classes that consume them.

**Hardware-Library-Class Mapping**

**Sources:** external/vesc/vescpacket.h28-34 external/pi-as5600/readme.md6-13 external/VL53L0X/tof.h25-37 communication/iso22133vehicleserver.h10-11

Refresh this wiki

This wiki was recently refreshed. Please wait 6 days to refresh again.