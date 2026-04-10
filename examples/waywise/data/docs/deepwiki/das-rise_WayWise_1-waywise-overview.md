# Source: https://deepwiki.com/das-rise/WayWise/1-waywise-overview

WayWise is a rapid prototyping library for connected and autonomous vehicles, developed by the **RISE Dependable Transport Systems** group README.md6-7 It is designed to facilitate research into functional safety, cybersecurity, and autonomous operations across various domains, including road traffic, agriculture, and maritime environments README.md7

Unlike production-grade stacks, WayWise focuses on flexibility and speed of development for both on-vehicle "brains" and desktop control applications README.md9-12 It serves as the foundation for several high-level projects, including **ControlTower** (a desktop ground station), **RCCar** (a physical RC car implementation), and **WayWiseR** (ROS2 integration) README.md14-17

The library is built on **C++** and the **Qt framework**, leveraging Qt's signal/slot mechanism and event loop for asynchronous communication and sensor processing README.md8 It follows a modular design where vehicles, sensors, and autopilots are decoupled through abstract interfaces, allowing for easy swapping of hardware components or simulation models.

WayWise is organized into several functional modules that work together to provide autonomous capabilities:

`PurePursuitWaypointFollower`

for trajectory tracking README.md46-47The following diagram illustrates how the major software components interact within a typical WayWise application.

**WayWise Component Interaction**

Sources: README.md9-11 README.md40-53

The library maps high-level autonomous concepts to specific C++ classes and namespaces. The diagram below shows the relationship between communication interfaces and the core vehicle logic.

**Protocol to Logic Mapping**

Sources: README.md10-11 README.md40-49 waywise.h11-12

WayWise is intended to be used as a **git submodule** within larger projects README.md30 It provides a set of examples to jumpstart development:

For detailed instructions on setting up the environment and running these examples, see **Getting Started & Examples**.

For a deep dive into the folder hierarchy, coding standards, and license information, see **Project Structure & Conventions**.

Refresh this wiki

This wiki was recently refreshed. Please wait 7 days to refresh again.