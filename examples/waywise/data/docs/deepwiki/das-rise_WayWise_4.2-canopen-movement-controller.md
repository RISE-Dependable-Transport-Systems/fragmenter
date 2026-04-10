# Source: https://deepwiki.com/das-rise/WayWise/4.2-canopen-movement-controller

The `CANopenMovementController`

provides a standardized interface for controlling industrial vehicles over a CAN bus using the CANopen protocol. It bridges the WayWise autopilot commands (speed and steering curvature) to hardware-level CAN messages, utilizing the **Lely CANopen** library for protocol stack management.

The CANopen implementation is split into three layers:

`MovementController`

subclass that integrates with `VehicleState`

and the autopilot update loop.The following diagram illustrates how autopilot commands flow from the WayWise core through the CANopen stack to the vehicle hardware.

"Movement Control Data Flow"

Sources: communication/CANopen/canopenmovementcontroller.cpp27-39 communication/CANopen/canopencontrollerinterface.cpp75-112 communication/CANopen/slave.cpp74-109

The `CANopenMovementController`

manages a dedicated `QThread`

for the CANopen event loop to ensure real-time communication does not block the main application UI or autopilot logic communication/CANopen/canopenmovementcontroller.cpp15-24

`sendCommandSpeed`

which eventually updates OD index `0x2000:01`

(km/h) and `0x2000:04`

(m/s) communication/CANopen/canopenmovementcontroller.cpp54-62 communication/CANopen/slave.cpp14-17`sendCommandSteeringCurvature`

which updates OD index `0x2000:02`

(Radius) and `0x2000:05`

(Curvature) communication/CANopen/canopenmovementcontroller.cpp46-52 communication/CANopen/slave.cpp20-23`VehicleState`

and calculates odometry based on the time delta since the last update communication/CANopen/canopenmovementcontroller.cpp82-96The controller monitors the `CANOpenAutopilotControlState`

via status bits received from the CAN bus communication/CANopen/canopenmovementcontroller.h17-24

Sources: communication/CANopen/canopenmovementcontroller.h26-70 communication/CANopen/canopenmovementcontroller.cpp102-117

The `CANopenControllerInterface`

initializes the Lely `io::Context`

, `ev::Loop`

, and `io::CanController`

communication/CANopen/canopencontrollerinterface.cpp75-97 It defaults to using the `can0`

interface communication/CANopen/canopencontrollerinterface.cpp95

The slave node is configured using the `cpp-slave.eds`

Electronic Data Sheet file with a default **Node ID of 2** communication/CANopen/canopencontrollerinterface.cpp99

| Object Index | Sub-index | Description | Direction | Data Type |
|---|---|---|---|---|
`0x2000` | 1 | Command Speed (km/h) | TPDO (To Vehicle) | `int8_t` |
`0x2000` | 5 | Command Curvature (1/m) | TPDO (To Vehicle) | `int32_t` (Scale 1e-4) |
`0x2001` | 1 | Control Status Bits | RPDO (From Vehicle) | `uint8_t` |
`0x2001` | 6 | Actual Speed (m/s) | RPDO (From Vehicle) | `int16_t` (Scale 0.01) |
`0x2001` | 7 | Actual Curvature (1/m) | RPDO (From Vehicle) | `int32_t` (Scale 1e-4) |
`0x2002` | 1 | GNSS Speed (cm/s) | TPDO (To Vehicle) | `int16_t` |

Sources: communication/CANopen/slave.cpp14-109 communication/CANopen/cpp-slave.eds93-97

The system is designed to run on a Raspberry Pi equipped with a **Seeed CAN-FD HAT**.

A known hardware bug in the Raspberry Pi I2C implementation can be triggered by the BNO055 IMU when using standard Seeed overlays communication/CANopen/misc/README1-2 To resolve this, a modified Device Tree Overlay (`seeed-can-fd-hat-v2-mod-overlay.dtbo`

) is provided which disables the hardware I2C used for the HAT's Real-Time Clock (RTC) while keeping CAN functionality intact communication/CANopen/misc/README3-7

If the controller fails to open the `can0`

device (e.g., hardware not present or interface down), it automatically switches to a simulation mode where speed and steering commands are fed directly back into the `VehicleState`

communication/CANopen/canopencontrollerinterface.cpp136-139 communication/CANopen/canopenmovementcontroller.cpp20-23

Sources: communication/CANopen/misc/README1-8 communication/CANopen/canopencontrollerinterface.cpp136-141

Refresh this wiki

This wiki was recently refreshed. Please wait 7 days to refresh again.