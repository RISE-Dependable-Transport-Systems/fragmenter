# Source: https://deepwiki.com/das-rise/WayWise/2.2-utility-classes

This section covers the foundational utility classes used throughout the WayWise codebase for system monitoring, data serialization, logging, and stream parsing. These utilities provide standardized mechanisms for handling common tasks such as monitoring Qt event-loop latency, managing binary data buffers, and routing system logs.

The `SimpleWatchdog`

class is designed to monitor the health of the Qt event loop. It detects instances where the event loop becomes "blocked" or sluggish, which is critical for real-time autopilot applications where timing jitter can lead to instability.

The watchdog operates by starting a `QTimer`

with a defined `timeout_ms`

core/simplewatchdog.cpp21 When the timer fires, it calculates the elapsed time since its last execution using `QTime::currentTime()`

core/simplewatchdog.cpp12-13

If the actual time taken exceeds the sum of the expected interval and a tolerance threshold (`timeout_tolerance_ms`

), it indicates that other tasks in the event loop are taking too long to process core/simplewatchdog.cpp15-16

`setTimeout(int value_ms)`

: Configures the base interval for the watchdog timer core/simplewatchdog.cpp29-33`setTimeoutTolerance(int value)`

: Sets the allowable jitter before a timeout is triggered core/simplewatchdog.cpp40-43`timeout(int timeTaken_ms)`

: A signal emitted when the event loop latency exceeds the threshold core/simplewatchdog.cpp17**Sources:** core/simplewatchdog.cpp1-44 core/simplewatchdog.h1-25

`VByteArray`

is a specialized subclass of `QByteArray`

core/vbytearray.h26 used primarily for binary serialization and deserialization. It is specifically tailored for protocols like VESC, where multi-byte integers and scaled doubles must be packed/unpacked in a specific endianness.

The class provides two main types of operations:

`vbAppendInt32`

or `vbAppendUint16`

take a value, split it into bytes (Big-Endian), and append them to the buffer core/vbytearray.cpp68-86`vbPopFrontInt32`

read bytes from the beginning of the buffer, reconstruct the value, and then A common pattern in WayWise communication is sending doubles as scaled integers to save bandwidth. `VByteArray`

automates this via:

`vbAppendDouble32(double number, double scale)`

: Multiplies the number by the scale and stores it as a 32-bit integer core/vbytearray.cpp119-122`vbPopFrontDouble32(double scale)`

: Reads a 32-bit integer and divides it by the scale to restore the double core/vbytearray.cpp278-281**Sources:** core/vbytearray.cpp1-282 core/vbytearray.h1-63

The `Logger`

class provides a centralized routing system for all `qDebug`

, `qInfo`

, `qWarning`

, and `qCritical`

messages. It implements a Singleton pattern logger/logger.cpp32-36 and integrates with the MAVLink severity levels.

When initialized, the logger intercepts Qt messages using `qInstallMessageHandler`

logger/logger.cpp66 Messages are processed in `messageOutput`

:

`stderr`

logger/logger.cpp114`initGroundStation()`

, logs are written to a `.log`

file in the "ControlTower Logs" documents folder logger/logger.cpp44-133`logSent`

signal is emitted, allowing other components (like a UI console or a MAVLink STATUSTEXT generator) to consume the logs logger/logger.cpp125This diagram shows how a standard Qt log call is transformed into various outputs.

| Log Source | Processing Entity | Output Destinations |
|---|---|---|
`qDebug()` | `Logger::messageOutput` | `stderr` |
`qWarning()` | `Logger::messageOutput` | `QFile (*.log)` |
`qCritical()` | `Logger::messageOutput` | `emit logSent()` |

**Sources:** logger/logger.cpp1-134 logger/logger.h1-40

The `JsonStreamParserTcp`

class is a specialized utility used to handle continuous streams of JSON data over a TCP socket. It is primarily utilized by the `DepthAiCamera`

to receive object detection data from OAK-D cameras.

The parser maintains a `QTcpSocket`

communication/jsonstreamparsertcp.cpp9 When data arrives, it splits the incoming buffer by the newline character `\n`

communication/jsonstreamparsertcp.cpp21 Each segment is then parsed into a `QJsonDocument`

.

The `DepthAiCamera`

class uses this parser to extract 3D coordinates (x, y, z) of detected objects.

| JSON Key | Coordinate Mapping | Note |
|---|---|---|
`depth_z` | `mCameraData.setX` | Forward distance in meters sensors/camera/depthaicamera.cpp28 |
`depth_x` | `mCameraData.setY` | Lateral offset (inverted) sensors/camera/depthaicamera.cpp29 |
`depth_y` | `mCameraData.setHeight` | Vertical offset sensors/camera/depthaicamera.cpp30 |

The following diagram illustrates the data flow from the raw TCP stream to the internal vehicle state.

Title: DepthAI JSON Stream Data Flow

**Sources:** communication/jsonstreamparsertcp.cpp1-43 sensors/camera/depthaicamera.cpp1-48

This diagram bridges the conceptual utility names with their specific class implementations and file locations.

Title: Utility Class Mapping

**Sources:** core/simplewatchdog.h9 core/vbytearray.h26 logger/logger.h13 communication/jsonstreamparsertcp.cpp5

Refresh this wiki

This wiki was recently refreshed. Please wait 7 days to refresh again.