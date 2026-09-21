# Raspberry Pi + Pixhawk

How to set up a Raspberry Pi as a companion computer for a Pixhawk flight
controller, so PX4 flight data shows up as ROS 2 topics on your network.

The Pi and the Pixhawk are connected by a serial cable. The Micro XRCE-DDS Agent
runs on the Pi and translates PX4's internal messages into ROS 2 topics. Any
computer on the same network can then subscribe to them.

The Pi runs headless on the drone, so everything here is done over SSH.

## How it works

```text
  Pixhawk                     Raspberry Pi                  Your computer
  (PX4 firmware)              (Ubuntu + ROS 2)              (Ubuntu + ROS 2)

  flight data                 MicroXRCEAgent                ros2 topic echo
      |                             |                              |
      +----- serial cable --------> + ------ Wi-Fi (DDS) --------> +
             921600 baud
```

The serial cable can only carry one protocol at a time. MAVLink and uXRCE-DDS both
want the same port, so you set it up twice: MAVLink first to check the wiring, then
uXRCE-DDS for the real bridge. That is why [MAVLink bridge](mavlink-bridge.md) and
[Micro XRCE-DDS Agent](xrce-dds-agent.md) are separate pages.

## What you need

| Item | Notes |
|---|---|
| Raspberry Pi Zero 2 W | Any Linux computer with a serial port works |
| Pixhawk 6C Mini | Any PX4 board with a spare telemetry port |
| microSD card | 16 GB or larger |
| TELEM2 cable | Cut and re-soldered by hand, see [Serial connection](serial-connection.md) |
| 2×20 header pins | The Pi Zero 2 W ships without them |
| micro-USB power supply | For bench testing |

| Software | Version |
|---|---|
| Operating system | Ubuntu Server 22.04.5 LTS, 64-bit |
| ROS 2 | Humble |
| PX4 | v1.14 or later |
| Micro XRCE-DDS Agent | Built from source |

ROS 2 Humble only runs on Ubuntu 22.04. Other Ubuntu versions have no
`ros-humble-*` packages, so this is not a free choice.

## Scope

This guide uses a Raspberry Pi Zero 2 W, but the companion computer can be any Linux
machine with a serial port. The ROS 2 install, the MAVLink test, the agent, and the
systemd service are all standard Linux and work anywhere.

Only two pages are Raspberry Pi specific:

- [Raspberry Pi setup](pi-setup.md), which uses Raspberry Pi Imager
- [Enabling the UART](serial-connection.md#enabling-the-uart-on-the-pi), which edits
  the Pi's boot files

On a different machine, skip those and use your own serial port name instead of
`/dev/serial0`.

The same goes for the flight controller. Any board running PX4 v1.14 or later with a
free telemetry port will work. Check its pinout against the
[wiring table](serial-connection.md#pinout) first.

## Useful links

- [PX4: Raspberry Pi Companion with Pixhawk](https://docs.px4.io/main/en/companion_computer/pixhawk_rpi)
- [ArduPilot: ROS 2 on Raspberry Pi](https://ardupilot.org/dev/docs/ros2-pi.html)
- [ROS 2 Humble install guide](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html)

```{toctree}
:maxdepth: 2
:caption: Setup

pi-setup
ros2-install
serial-connection
```

```{toctree}
:maxdepth: 2
:caption: PX4 integration

mavlink-bridge
xrce-dds-agent
ground-station
autostart
```

```{toctree}
:maxdepth: 2
:caption: Reference

troubleshooting
```
