# WayWise GNSS Spoofing Exploitation Plan and C++ Test Implementation

Analyze the WayWise codebase for a critical GNSS-based vulnerability and generate a detailed exploitation plan with a complete C++ test file.

## Scenario Context

The vehicle operates in zones with different speed limits (e.g., 30 km/h in residential areas, 80 km/h on highways). The system uses GNSS (GPS/GLONASS) signals to determine the vehicle's current position and automatically enforces the speed limit for that zone.

## Target Vulnerability

Focus on: **GNSS Position Spoofing to Bypass Speed Limit Enforcement**

The vehicle trusts GNSS position data without verification, allowing an attacker to spoof the vehicle's perceived location to report being in a high-speed zone when actually in a low-speed zone (or vice versa).

## Required Output

### 1. Detailed Exploitation Plan

Provide a comprehensive exploitation plan including:

**Attack Prerequisites:**

- Attacker's required access level (physical access, network access, proximity)

- Required equipment or software tools

- Environmental conditions needed

**Attack Steps (Detailed Sequence):**

1. Reconnaissance: How to identify the target system and its GNSS receiver configuration

2. Interception: How to monitor current GNSS signals and vehicle position data flow

3. Spoofing Setup: Technical steps to generate fake GNSS signals or inject false position data

4. Exploitation: How to manipulate the vehicle's perceived position to change speed limit zones

5. Persistence: How to maintain the spoofed position without detection

6. Impact Amplification: How to maximize the effect (e.g., reporting highway position in residential zone)

**Technical Details:**

- GNSS signal structure and parameters to spoof

- WayWise communication protocols involved

- Specific code paths in WayWise that process position data

- Data validation (or lack thereof) in the position processing pipeline

**Expected Impact:**

- Vehicle exceeds safe speed limits in restricted zones

- Safety systems fail to prevent dangerous maneuvers

- Potential for accidents or regulatory violations

**Detection Evasion:**

- How the attack avoids logging or alerting systems

- Techniques to make spoofed data appear legitimate

### 2. C++ Test Implementation (main.cpp)

Generate a complete, compilable C++ file that demonstrates this vulnerability:

```cpp

// Structure the code with these components:



// 1. Simulated GNSS spoofing function

//    - Generates fake position coordinates

//    - Mimics legitimate GNSS signal structure



// 2. Position data injection function

//    - Injects spoofed coordinates into WayWise system

//    - Bypasses any validation mechanisms



// 3. Speed limit verification function

//    - Checks what speed limit the system enforces

//    - Verifies the vulnerability is exploitable



// 4. Attack demonstration function

//    - Simulates vehicle in 30 km/h zone (actual position)

//    - Spoofs position to 80 km/h zone

//    - Shows system incorrectly allows high speed



// 5. Main function with clear test output

//    - Runs the complete attack simulation

//    - Reports success/failure of exploitation

//    - Demonstrates safety impact

```

A working baseline C++ file is shown below. Fill in the functions with appropriate logic to simulate the GNSS spoofing attack as per the exploitation plan.

```cpp
#include <QCoreApplication>
#include <QSerialPortInfo>
#include <QDateTime>
#include <QFile>
#include <signal.h>
#include <QProcess>
#include <QCommandLineParser>
#include <QJsonDocument>
#include <QJsonObject>
#include <random>
#include "WayWise/core/simplewatchdog.h"
#include "WayWise/vehicles/carstate.h"
#include "WayWise/vehicles/controller/carmovementcontroller.h"
#include "WayWise/sensors/imu/bno055orientationupdater.h"
#include "WayWise/sensors/gnss/ubloxrover.h"
#include "WayWise/autopilot/waypointfollower.h"
#include "WayWise/autopilot/purepursuitwaypointfollower.h"
#include "WayWise/vehicles/controller/vescmotorcontroller.h"
#include "WayWise/sensors/camera/depthaicamera.h"
#include "WayWise/sensors/fusion/sdvpvehiclepositionfuser.h"
#include "WayWise/sensors/gnss/rtcmclient.h"
#include "WayWise/communication/mavsdkvehicleserver.h"
#include "WayWise/communication/parameterserver.h"
#include "WayWise/logger/logger.h"
#include "WayWise/sensors/angle/as5600updater.h"
#include "WayWise/vehicles/truckstate.h"
#include "WayWise/vehicles/trailerstate.h"
#include "WayWise/routeplanning/routeutils.h"
#include <QDir>
#include <QStandardPaths>
#include <unistd.h>
#include <limits.h>
#include <string>

static void terminationSignalHandler(int signal) {
    qDebug() << "Shutting down";
    if (signal==SIGINT || signal==SIGTERM || signal==SIGQUIT || signal==SIGHUP)
        qApp->quit();
}

// static std::mt19937 rng{std::random_device{}()};
static std::mt19937 rng{12345};

auto gaussianGnssPerturbationFn =
[](QTime simTime,
   QSharedPointer<VehicleState> vehicleState,
   std::normal_distribution<double>& noise_pos,
   std::normal_distribution<double>& noise_yaw,
   std::mt19937& rng)
{
    Q_UNUSED(simTime);
    PosPoint gnssPosition = vehicleState->getPosition(PosType::GNSS);

    double dx = noise_pos(rng);
    double dy = noise_pos(rng);
    double dyaw = noise_yaw(rng);

    gnssPosition.setX(gnssPosition.getX() + dx);
    gnssPosition.setY(gnssPosition.getY() + dy);
    gnssPosition.setYaw(gnssPosition.getYaw() + dyaw);

    vehicleState->setPosition(gnssPosition);
    return true;
};

// Get executable directory
std::string getExecutableDir() {
    char buffer[PATH_MAX];
    ssize_t len = readlink("/proc/self/exe", buffer, sizeof(buffer)-1);
    if (len != -1) {
        buffer[len] = '\0';
        std::string fullPath(buffer);
        return fullPath.substr(0, fullPath.find_last_of('/'));
    }
    return ".";
}

// Determine base path: PROJECT_ROOT if exists, otherwise exec dir
QString determineBasePath() {
#ifdef PROJECT_ROOT
    QDir projectRoot(QString(PROJECT_ROOT));
    if (projectRoot.exists())
        return projectRoot.absolutePath();
#endif
    return QString::fromStdString(getExecutableDir());
}

QString fixPath(const QString &path, const QString &basePath)
{
    if (path.isEmpty())
        return "";

    QFileInfo fi(path);
    if (fi.isAbsolute()) {
        return fi.absoluteFilePath();
    } else {
        QDir base(basePath);
        return base.absoluteFilePath(path);
    }
}

// ----------------------------------------------------
// Config struct to hold all settings
// ----------------------------------------------------
struct TruckConfig {
    int truckId = 1;
    int trailerId = 25;
    bool attachTrailer = false;
    QString configPath;

    // Additional configurable parameters
    double truckLength = 0.5;
    double truckWidth = 0.21;
    double trailerLength = 0.96;
    double trailerWidth = 0.21;
    double trailerWheelBase = 0.64;
    double axisDistance = 0.3;
    double turnRadius = 0.67;
    double servoCenter = 0.5;
    double servoRange = 0.50;
    double angleSensorOffset = 94.043;
    double purePursuitRadius = 1.0;
    double speedToRPMFactor = 5190;
    bool adaptiveRadius = true;
    bool repeatRoute = false;
    bool useVescIMU = true;
    int updateVehicleStatePeriodMs = 25;
    QString controlTowerIP = "127.0.0.1";
    int controlTowerPort = 14540;
    QString rtcmInfoFilePath = "";
    QString speedLimitRegionsFilePath = "";
    QString enuRef = "57.7171924432987, 12.962759215969157, 0.0";
    QString routeFilePath = "";
    double gnssSimulationNoiseSigmaPos = 0.0; // meters
    double gnssSimulationNoiseSigmaYaw = 0.0; // radians
    QString logDirectoryPath = "";   // if empty, Documents directory (OS agnostic) is used
};

// ----------------------------------------------------
// Helper functions
// ----------------------------------------------------
TruckConfig loadConfigFromJson(const QString &path)
{
    TruckConfig config;
    QFile file(path);
    if (file.exists() && file.open(QIODevice::ReadOnly)) {
        QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
        file.close();
        if (doc.isObject()) {
            QJsonObject obj = doc.object();
            config.truckId = obj.value("truck_id").toInt(config.truckId);
            config.trailerId = obj.value("trailer_id").toInt(config.trailerId);
            config.attachTrailer = obj.value("attach_trailer").toBool(config.attachTrailer);

            config.truckLength = obj.value("truck_length").toDouble(config.truckLength);
            config.truckWidth = obj.value("truck_width").toDouble(config.truckWidth);
            config.trailerLength = obj.value("trailer_length").toDouble(config.trailerLength);
            config.trailerWidth = obj.value("trailer_width").toDouble(config.trailerWidth);
            config.trailerWheelBase = obj.value("trailer_wheelbase").toDouble(config.trailerWheelBase);
            config.axisDistance = obj.value("axis_distance").toDouble(config.axisDistance);
            config.turnRadius = obj.value("turn_radius").toDouble(config.turnRadius);
            config.servoCenter = obj.value("servo_center").toDouble(config.servoCenter);
            config.servoRange = obj.value("servo_range").toDouble(config.servoRange);
            config.angleSensorOffset = obj.value("angle_sensor_offset").toDouble(config.angleSensorOffset);
            config.purePursuitRadius = obj.value("pure_pursuit_radius").toDouble(config.purePursuitRadius);
            config.speedToRPMFactor = obj.value("speed_to_rpm_factor").toDouble(config.speedToRPMFactor);
            config.adaptiveRadius = obj.value("adaptive_radius").toBool(config.adaptiveRadius);
            config.repeatRoute = obj.value("repeat_route").toBool(config.repeatRoute);
            config.useVescIMU = obj.value("use_vesc_imu").toBool(config.useVescIMU);
            config.updateVehicleStatePeriodMs = obj.value("update_period_ms").toInt(config.updateVehicleStatePeriodMs);
            config.controlTowerIP = obj.value("control_tower_ip").toString(config.controlTowerIP);
            config.controlTowerPort = obj.value("control_tower_port").toInt(config.controlTowerPort);
            config.rtcmInfoFilePath = obj.value("rtcm_info_file_path").toString(config.rtcmInfoFilePath);
            config.speedLimitRegionsFilePath = obj.value("speed_limit_regions_file_path").toString(config.speedLimitRegionsFilePath);
            config.enuRef = obj.value("enu_ref").toString(config.enuRef);
            config.routeFilePath = obj.value("route_file_path").toString(config.routeFilePath);
            config.gnssSimulationNoiseSigmaPos = obj.value("gnss_simulation_noise_sigma_pos").toDouble(config.gnssSimulationNoiseSigmaPos);
            config.gnssSimulationNoiseSigmaYaw = obj.value("gnss_simulation_noise_sigma_yaw").toDouble(config.gnssSimulationNoiseSigmaYaw);
            config.logDirectoryPath = obj.value("log_directory_path").toString(config.logDirectoryPath);
        }
    }
    return config;
}

TruckConfig parseArguments(QCoreApplication &app)
{
    TruckConfig config;

    QCommandLineParser parser;
    parser.setApplicationDescription("RC Truck configuration");
    parser.addHelpOption();

    QCommandLineOption configFileOption({"c", "config"}, "Path to JSON config file.", "file");
    parser.addOption(configFileOption);

    QCommandLineOption truckIDOption({"i", "truck-id"}, "Truck ID.", "id", QString::number(config.truckId));
    parser.addOption(truckIDOption);

    QCommandLineOption trailerIDOption({"l", "trailer-id"}, "Trailer ID.", "id", QString::number(config.trailerId));
    parser.addOption(trailerIDOption);

    QCommandLineOption attachTrailerOption({"a", "attach-trailer"}, "Attach trailer to truck (flag).");
    parser.addOption(attachTrailerOption);

    parser.process(app);

    config.configPath = parser.value(configFileOption);
    if (!config.configPath.isEmpty())
        config = loadConfigFromJson(config.configPath);

    if (parser.isSet(truckIDOption))
        config.truckId = parser.value(truckIDOption).toInt();

    if (parser.isSet(trailerIDOption))
        config.trailerId = parser.value(trailerIDOption).toInt();

    if (parser.isSet(attachTrailerOption))
        config.attachTrailer = true;

    QString basePath = determineBasePath();

    config.rtcmInfoFilePath = fixPath(config.rtcmInfoFilePath, basePath);
    config.speedLimitRegionsFilePath = fixPath(config.speedLimitRegionsFilePath, basePath);
    config.routeFilePath = fixPath(config.routeFilePath, basePath);
    config.logDirectoryPath = fixPath(config.logDirectoryPath, basePath);

    return config;
}


// ----------------------------------------------------
// Main
// ----------------------------------------------------
int main(int argc, char *argv[])
{
    Logger::initVehicle();

    QCoreApplication app(argc, argv);

    TruckConfig config = parseArguments(app);

    // --- Vehicle setup ---
    QTimer mUpdateVehicleStateTimer;
    QSharedPointer<TruckState> mTruckState = QSharedPointer<TruckState>::create(config.truckId);
    mTruckState->setLength(config.truckLength);
    mTruckState->setWidth(config.truckWidth);
    mTruckState->setAxisDistance(config.axisDistance);
    mTruckState->setMaxSteeringAngle(atan(config.axisDistance / config.turnRadius));
    QStringList parts = config.enuRef.split(",");
    if (parts.size() == 3) {
        double lat = parts[0].toDouble();
        double lon = parts[1].toDouble();
        double alt = parts[2].toDouble();
        mTruckState->setEnuRef({lat, lon, alt});
    }

    QSharedPointer<TrailerState> mTrailerState;
    if (config.attachTrailer) {
        mTrailerState = QSharedPointer<TrailerState>::create(config.trailerId);
        mTrailerState->setWheelBase(config.trailerWheelBase);
        mTrailerState->setLength(config.trailerLength);
        mTrailerState->setWidth(config.trailerWidth);
        mTruckState->setTrailingVehicle(mTrailerState);
    }

    MavsdkVehicleServer mavsdkVehicleServer(mTruckState, QHostAddress(config.controlTowerIP), config.controlTowerPort);

    // --- Lower-level control setup ---
    QSharedPointer<CarMovementController> mCarMovementController(new CarMovementController(mTruckState));
    mCarMovementController->setSpeedToRPMFactor(config.speedToRPMFactor);
    // setup and connect VESC, simulate movements if unable to connect
    QSharedPointer<VESCMotorController> mVESCMotorController(new VESCMotorController());
    foreach(const QSerialPortInfo &portInfo, QSerialPortInfo::availablePorts()) {
        if (portInfo.description().toLower().replace("-", "").contains("chibios")) { // assumption: Serial device with ChibiOS in description is VESC
            mVESCMotorController->connectSerial(portInfo);
            qDebug() << "VESCMotorController connected to:" << portInfo.systemLocation();
        }
    }
    if (mVESCMotorController->isSerialConnected()) {
        mCarMovementController->setMotorController(mVESCMotorController);

        // VESC is a special case that can also control the servo
        const auto servoController = mVESCMotorController->getServoController();
        servoController->setInvertOutput(true);
        // NOTE: HEADSTART rc car (values read from sdvp pcb)
        servoController->setServoRange(config.servoRange);
        servoController->setServoCenter(config.servoCenter);
        mCarMovementController->setServoController(servoController);
    } else {
        QObject::connect(&mUpdateVehicleStateTimer, &QTimer::timeout, [&](){
            mCarMovementController->simulationStep(config.updateVehicleStatePeriodMs);
        });
        mUpdateVehicleStateTimer.start(config.updateVehicleStatePeriodMs);
    }

    // --- Positioning setup ---
    // Position Fuser
    SDVPVehiclePositionFuser positionFuser;

    // GNSS (with fused IMU when using u-blox F9R)
    QSharedPointer<GNSSReceiver> mGNSSReceiver;
    foreach(const QSerialPortInfo &portInfo, QSerialPortInfo::availablePorts()) {
        if (portInfo.manufacturer().toLower().replace("-", "").contains("ublox")) {
            QSharedPointer<UbloxRover> mUbloxRover(new UbloxRover(mTruckState));
            if (mUbloxRover->connectSerial(portInfo)) {
                qDebug() << "UbloxRover connected to:" << portInfo.systemLocation();

                mUbloxRover->setChipOrientationOffset(0.0, 0.0, 0.0);
                QObject::connect(mUbloxRover.get(), &UbloxRover::updatedGNSSPositionAndYaw, &positionFuser, &SDVPVehiclePositionFuser::correctPositionAndYawGNSS);

                mUbloxRover->setReceiverVariant(RECEIVER_VARIANT::UBLX_ZED_F9R); // or UBLX_ZED_F9P
                mavsdkVehicleServer.setUbloxRover(mUbloxRover);

                // -- NTRIP/TCP client setup for feeding RTCM data into GNSS receiver
                RtcmClient rtcmClient;
                QObject::connect(mUbloxRover.get(), &UbloxRover::gotNmeaGga, &rtcmClient, &RtcmClient::forwardNmeaGgaToServer);
                QObject::connect(&rtcmClient, &RtcmClient::rtcmData, mUbloxRover.get(), &UbloxRover::writeRtcmToUblox);
                // QObject::connect(&rtcmClient, &RtcmClient::baseStationPosition, mTruckState.get(), &TruckState::setEnuRef);
                if (rtcmClient.connectWithInfoFromFile(config.rtcmInfoFilePath))
                    qDebug() << "RtcmClient: connected to" << QString(rtcmClient.getCurrentHost()+ ":" + QString::number(rtcmClient.getCurrentPort()));
                else
                    qDebug() << "RtcmClient: not connected";

                mGNSSReceiver = mUbloxRover;
            }
        }
    }

    if (!mGNSSReceiver) {
        qDebug() << "No GNSS receiver connected. Simulating GNSS data.";
        mGNSSReceiver.reset(new GNSSReceiver(mTruckState));
        mGNSSReceiver->setReceiverVariant(RECEIVER_VARIANT::WAYWISE_SIMULATED);
        mGNSSReceiver->setReceiverState(RECEIVER_STATE::READY);

        QObject::connect(mCarMovementController.get(), &CarMovementController::updatedOdomPositionAndYaw, [&](QSharedPointer<VehicleState> vehicleState, double distanceDriven){
            bool fused;
            if (config.gnssSimulationNoiseSigmaPos != 0.0 || config.gnssSimulationNoiseSigmaYaw != 0.0) {
                static std::normal_distribution<double> noise_pos(0.0, config.gnssSimulationNoiseSigmaPos);
                static std::normal_distribution<double> noise_yaw(0.0, config.gnssSimulationNoiseSigmaYaw);

                fused = mGNSSReceiver->simulationStep(
                    [=](QTime simTime, QSharedPointer<VehicleState> vehicleState) mutable -> bool
                    {
                        return gaussianGnssPerturbationFn(simTime, vehicleState, noise_pos, noise_yaw, rng);
                    }
                );
            } else {
                fused = mGNSSReceiver->simulationStep();
            }
            positionFuser.correctPositionAndYawGNSS(vehicleState, distanceDriven, fused);
        });
    }

    // IMU
    QSharedPointer<IMUOrientationUpdater> mIMUOrientationUpdater;
    if (config.useVescIMU)
        mIMUOrientationUpdater = mVESCMotorController->getIMUOrientationUpdater(mTruckState);
    else
        mIMUOrientationUpdater.reset(new BNO055OrientationUpdater(mTruckState, "/dev/i2c-1"));
    QObject::connect(mIMUOrientationUpdater.get(), &IMUOrientationUpdater::updatedIMUOrientation, &positionFuser, &SDVPVehiclePositionFuser::correctPositionAndYawIMU);

    // Angle Sensor
    QSharedPointer<AngleSensorUpdater> mAngleSensorUpdater;
    mAngleSensorUpdater.reset(new AS5600Updater(mTruckState, config.angleSensorOffset));
    mTruckState->setSimulateTrailer(!mAngleSensorUpdater->isConnected());

    // Odometry
    QObject::connect(mCarMovementController.get(), &CarMovementController::updatedOdomPositionAndYaw, &positionFuser, &SDVPVehiclePositionFuser::correctPositionAndYawOdom);

    // --- Autopilot ---
    QSharedPointer<PurepursuitWaypointFollower> mWaypointFollower(new PurepursuitWaypointFollower(mCarMovementController));
    mWaypointFollower->setPurePursuitRadius(config.purePursuitRadius);
    mWaypointFollower->setRepeatRoute(config.repeatRoute);
    mWaypointFollower->setAdaptivePurePursuitRadiusActive(config.adaptiveRadius);

    mWaypointFollower->loadSpeedLimitRegionsFile(config.speedLimitRegionsFilePath);

    QObject::connect(mTruckState.get(), &TruckState::updatedEnuReference, [&](llh_t mEnuReference) {
        Q_UNUSED(mEnuReference)
        qInfo() << "New ENU reference received, reloading speed limit regions.";

        mWaypointFollower->clearSpeedLimitRegions();
        mWaypointFollower->loadSpeedLimitRegionsFile(config.speedLimitRegionsFilePath);
    });

    // Setup MAVLINK communication towards ControlTower
    mavsdkVehicleServer.setMovementController(mCarMovementController);
    mavsdkVehicleServer.setWaypointFollower(mWaypointFollower);

    // Advertise parameters
    mTruckState->provideParametersToParameterServer();
    if (config.attachTrailer) {
        mTrailerState->provideParametersToParameterServer();
    }
    mavsdkVehicleServer.provideParametersToParameterServer();
    mWaypointFollower->provideParametersToParameterServer();

    // Watchdog that warns when EventLoop is slowed down
    SimpleWatchdog watchdog;

    /* --- Logging of Experiments --- */
    QString logDirectoryPath;

    if (!config.logDirectoryPath.isEmpty()) {
        // Use config override
        logDirectoryPath = config.logDirectoryPath;
    } else {
        // Fallback to Documents/PRECISE Experiments
        QDir documentsDirectory(QStandardPaths::writableLocation(QStandardPaths::DocumentsLocation));
        logDirectoryPath = documentsDirectory.filePath("PRECISE Experiments");
    }
    logDirectoryPath = logDirectoryPath.replace(QRegularExpression("[/\\\\]+$"), "");

    // Ensure folder exists
    QDir dir;
    if (!dir.exists(logDirectoryPath)) {
        if (dir.mkpath(logDirectoryPath))
            qDebug() << "Created log directory:" << logDirectoryPath;
        else
            qWarning() << "Failed to create log directory:" << logDirectoryPath;
    }

    // Create the file
    QFile* logFile = new QFile;
    QString fileName = QString("%1/Log %2.log").arg(logDirectoryPath).arg(QDateTime::currentDateTime().toString("dd-MM-yyyy hh-mm-ss"));
    logFile->setFileName(fileName);

    logFile->open(QIODevice::Append | QIODevice::Text); // Open file in append mode with text handling

    // Create the timer
    QTimer logTimer;
    double printInterval_ms = 1000;

    QObject::connect(&logTimer, &QTimer::timeout, [&](){    // Executes on each timeout

        // Parameters to log
        const double speed = mTruckState->getSpeed();
        const PosPoint gnssPosition = mTruckState->getPosition(PosType::fused);
        const PosPoint targetWaypoint = mWaypointFollower->getCurrentGoal();

        QString textToAppend = QString("%1 | Current speed = %2 m/s | GNSS position: Lat = %3 Lon = %4 Yaw = %5 | Target waypoint: X = %6 Y = %7 Speed = %8\n")
                                   .arg(QDateTime::currentDateTime().toString("dd-MM-yyyy hh:mm:ss"))
                                   .arg(speed)
                                   .arg(gnssPosition.getX())
                                   .arg(gnssPosition.getY())
                                   .arg(gnssPosition.getYaw())
                                   .arg(targetWaypoint.getX())
                                   .arg(targetWaypoint.getY())
                                   .arg(targetWaypoint.getSpeed());

        logFile->write(textToAppend.toLocal8Bit());
        logFile->flush();   // Ensures data is written
    });
    logTimer.start(printInterval_ms);
    qInfo() << "Logging to:" << QFileInfo(fileName).absoluteFilePath();

    /* --- Logging of Experiments END --- */

    // Read route and start waypoint follower after 2 seconds
    QTimer::singleShot(2000, [&]() {
        if (mTruckState->getSpeed() < 0.1 && !config.routeFilePath.isEmpty()) {

            if (!QFile::exists(config.routeFilePath)) {
                qWarning() << "Route file does not exist:" << config.routeFilePath;
                return;
            }

            qInfo() << "Reading route from file:" << config.routeFilePath
                    << "using ENU reference:"
                    << mTruckState->getEnuRef().latitude << ","
                    << mTruckState->getEnuRef().longitude << ","
                    << mTruckState->getEnuRef().height;

            QList<PosPoint> waypointList = readRouteFromFile(config.routeFilePath, mTruckState->getEnuRef());

            mWaypointFollower->clearRoute();
            mWaypointFollower->resetState();
            mWaypointFollower->addRoute(waypointList);
            mWaypointFollower->startFollowingRoute(false);

            qDebug() << "Started waypoint follower with a route of " << waypointList.size() << " waypoints";
        }
    });

    // Perform safe shutdown
    signal(SIGINT, terminationSignalHandler);
    QObject::connect(&app, &QCoreApplication::aboutToQuit, [&](){
        mGNSSReceiver->aboutToShutdown();
        ParameterServer::getInstance()->saveParametersToXmlFile("vehicle_parameters.xml");
        logFile->close();
    });
    QObject::connect(&mavsdkVehicleServer, &MavsdkVehicleServer::shutdownOrRebootOnboardComputer, [&](bool isShutdown){
        qApp->quit();
        if (isShutdown) {
           qDebug() << "\nSystem shutdown...";
           QProcess::startDetached("sudo", QStringList() << "shutdown" << "-P" << "now");
        }else {
           qDebug() << "\nSystem reboot...";
           QProcess::startDetached("sudo", QStringList() << "shutdown" << "-r" << "now");
        }
    });

    qDebug() << "                    _________________________________________________";
    qDebug() << "            /|     |                                                 |";
    qDebug() << "            ||     |                                                 |";
    qDebug() << "       .----|-----,|                                                 |";
    qDebug() << "       ||  ||   ==||                                                 |";
    qDebug() << "  .-----'--'|   ==||                                                 |";
    qDebug() << "  |)-      ~|     ||_________________________________________________|";
    qDebug() << "  | ___     |     |____...==..._  >\\______________________________|";
    qDebug() << " [_/.-.\\---\\\\-----  //.-.  .-.\\\\    |/            \\\\ .-.  .-. //";
    qDebug() << "   ( o )   ===~~~~   ( o )( o )     o               ( o )( o )";
    qDebug() << "    '-'               '-'  '-'                       '-'  '-'\n";

    return app.exec();
}
```

### 3. Risk Assessment

Provide:

- **Severity Rating**: Critical/High/Medium/Low with justification

- **Likelihood**: Probability of this attack occurring in real-world deployment

- **Safety Impact**: Potential consequences (injury, property damage, regulatory)

- **Attack Complexity**: Technical skill and resources required

### 4. Mitigation Strategies

Provide specific, implementable countermeasures:

- GNSS signal authentication and integrity checking

- Multi-sensor fusion (compare GNSS with IMU, odometry, vision)

- Anomaly detection for position jumps or impossible movements

- Secure communication channels for position data

- Code-level input validation and sanitization

- Redundant safety systems independent of GNSS

### 5. Code-Level Fixes

Point to specific locations in WayWise codebase where fixes should be applied, with example code snippets showing:

- Where to add GNSS signal validation

- How to implement position sanity checks

- Where to add sensor fusion logic

Generate the complete exploitation plan and C++ test code with detailed inline comments explaining each attack step.
