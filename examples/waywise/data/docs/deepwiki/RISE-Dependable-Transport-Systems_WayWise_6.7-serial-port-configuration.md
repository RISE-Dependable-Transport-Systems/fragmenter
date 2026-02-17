# Source: https://deepwiki.com/RISE-Dependable-Transport-Systems/WayWise/6.7-serial-port-configuration

The Serial Port Configuration system provides a user interface for selecting and configuring serial port connections to vehicles and GNSS receivers. The `SerialPortDialog`

class is a Qt-based dialog that discovers available serial ports, displays their information, allows baud rate configuration, and emits connection parameters for use by communication subsystems.

For information about how serial connections are established and managed after configuration, see Ground Station (MavsdkStation). For GNSS-specific serial configuration, see GNSS & RTK Positioning.

The serial port configuration system consists of three primary components:

**Sources:** userinterface/serialportdialog.h1-40 userinterface/serialportdialog.cpp1-59 communication/vehicleconnections/mavsdkstation.h27-28

The dialog queries the operating system for available serial ports using Qt's `QSerialPortInfo`

class, presents them to the user with descriptive information, and emits the selected configuration for connection establishment.

**Sources:** userinterface/serialportdialog.h16-37 userinterface/serialportdialog.cpp11-27

The dialog displays available serial ports in a `QListWidget`

, with each entry showing:

| Component | Description | Source |
|---|---|---|
systemLocation | Device path (e.g., `/dev/ttyUSB0` ) | Primary identifier |
manufacturer | Hardware manufacturer name | Metadata |
description | Device description | Metadata |

The list is populated dynamically each time the dialog is shown via the `showEvent()`

override:

**Sources:** userinterface/serialportdialog.cpp41-58

The implementation at userinterface/serialportdialog.cpp46-57 shows the port discovery and list population:

`QSerialPortInfo::availablePorts()`

to query system`QSerialPortInfo`

object in item's `Qt::UserRole`

dataThe baud rate is configured through a `QComboBox`

populated with standard baud rates:

| Standard Baud Rates | Common Use Cases |
|---|---|
| 9600 | Legacy devices |
| 19200 | Low-speed sensors |
| 38400 | Standard serial |
| 57600 | Default - MAVSDK default |
| 115200 | High-speed MAVLink |
| 230400, 460800, 921600 | High-throughput applications |

**Sources:** userinterface/serialportdialog.cpp19-21

The combo box is populated at construction time with all values returned by `QSerialPortInfo::standardBaudRates()`

, with 57600 selected as the default.

| Button | Icon | Action | Implementation |
|---|---|---|---|
Add connection | `SP_DialogOkButton` | Emit `selectedSerialPort` signal | serialportdialog.cpp29-33 |
Cancel | `SP_DialogCancelButton` | Hide dialog without action | serialportdialog.cpp35-38 |

**Sources:** userinterface/serialportdialog.cpp16-17 userinterface/serialportdialog.ui76-87

**Sources:** userinterface/serialportdialog.cpp29-33 communication/vehicleconnections/mavsdkstation.cpp36-46

The dialog uses Qt's signal-slot mechanism to decouple UI from connection logic:

**Sources:** userinterface/serialportdialog.h24-25 communication/vehicleconnections/mavsdkstation.h28

The signal signature at userinterface/serialportdialog.h25 passes both the port information object and the selected baud rate as separate parameters, allowing the receiver to access all necessary connection details.

The dialog layout is defined in Qt Designer format at userinterface/serialportdialog.ui1-96 The structure consists of:

**Sources:** userinterface/serialportdialog.ui16-91

The layout uses spacers to right-align the baud rate selector and action buttons, providing a clean, standard dialog appearance.

The `MavsdkStation`

class provides the `startListeningSerial()`

method that consumes the configuration from `SerialPortDialog`

:

| Parameter | Type | Purpose |
|---|---|---|
`portInfo` | `const QSerialPortInfo&` | Port identification and metadata |
`baudrate` | `int` | Communication speed |

**Implementation:** communication/vehicleconnections/mavsdkstation.cpp36-46

The method:

`systemLocation()`

from `QSerialPortInfo`

(e.g., `/dev/ttyUSB0`

)`std::string`

for MAVSDK C++ interface`mMavsdk->add_serial_connection(location, baudrate)`

`ConnectionResult`

for success/failureThe `MavsdkStation`

header at communication/vehicleconnections/mavsdkstation.h28 defines default parameters:

These defaults align with common Linux serial device naming (`ttyUSB0`

) and MAVSDK's standard serial baud rate.

**Sources:** communication/vehicleconnections/mavsdkstation.h28 communication/vehicleconnections/mavsdkstation.cpp36-46

**Sources:** userinterface/serialportdialog.cpp41-58 userinterface/serialportdialog.cpp29-33 communication/vehicleconnections/mavsdkstation.cpp36-46

| Use Case | Port Type | Typical Baudrate | Description |
|---|---|---|---|
Vehicle MAVLink | USB-Serial adapter | 57600 or 115200 | Ground station to vehicle communication |
GNSS Receiver | USB-Serial (u-blox) | 115200 or 230400 | High-speed GNSS data (NAV-PVT, ESF messages) |
Radio Telemetry | USB radio modem | 57600 | Long-range wireless MAVLink |
Debug Console | FTDI/CP2102 | 115200 | Vehicle onboard computer serial debug |

The dialog uses Qt's meta-object system to store the full `QSerialPortInfo`

object:

**Sources:** userinterface/serialportdialog.cpp48-51

At userinterface/serialportdialog.cpp9 `Q_DECLARE_METATYPE(QSerialPortInfo)`

registers the type with Qt's meta-object system, enabling storage in `QVariant`

.

At userinterface/serialportdialog.cpp31 the stored data is retrieved and extracted:

When no serial ports are available:

**Sources:** userinterface/serialportdialog.cpp54-57

The `SerialPortDialog`

follows Qt's threading model:

Since both `SerialPortDialog`

and `MavsdkStation`

typically exist on the main thread, the signal-slot connection is direct (not queued). The MAVSDK library handles internal threading for serial I/O.

**Sources:** userinterface/serialportdialog.cpp29-33 communication/vehicleconnections/mavsdkstation.cpp9-21

The Serial Port Configuration system provides:

| Feature | Implementation | Location |
|---|---|---|
Port Discovery | `QSerialPortInfo::availablePorts()` | serialportdialog.cpp46 |
Port Metadata | systemLocation, manufacturer, description | serialportdialog.cpp48 |
Baud Rate Selection | Standard rates from Qt, default 57600 | serialportdialog.cpp19-21 |
Configuration Output | `selectedSerialPort(QSerialPortInfo, qint32)` signal | serialportdialog.h25 |
Connection Establishment | `MavsdkStation::startListeningSerial()` | mavsdkstation.cpp36-46 |
Error Handling | Empty list detection, disabled button | serialportdialog.cpp54-57 |

The dialog serves as the primary entry point for serial-based vehicle and GNSS connections in the WayWise ground station application.

Refresh this wiki
