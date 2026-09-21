# Raspberry Pi Companion Computer for PX4

Setting up a Raspberry Pi Zero 2 W as a companion computer for a Pixhawk 6C Mini
running PX4. The two boards are joined by a serial link between the Pixhawk's
TELEM2 port and the Pi's UART pins. On top of that link, the Micro XRCE-DDS Agent
bridges PX4's internal uORB messages onto the ROS 2 network, so flight and sensor
data appear as ROS 2 topics that any machine on the network can subscribe to.

The Pi runs headless on the drone. Everything below is done over SSH.

## How the pieces fit together

```text
  Pixhawk 6C Mini                 Raspberry Pi Zero 2 W            Ground station
  (PX4 firmware)                  (Ubuntu 22.04 + ROS 2)           (Ubuntu 22.04 + ROS 2)

  uORB topics                     MicroXRCEAgent                   ros2 topic echo
      |                                 |                                  |
      +--- uxrce_dds_client ---> TELEM2 serial link ---> DDS over Wi-Fi ----+
                                  921600 baud
```

The serial link carries **one** protocol at a time. MAVLink and uXRCE-DDS both want
TELEM2, so the PX4 parameters get switched between the two — MAVLink first to prove
the wiring works, then uXRCE-DDS for the real bridge. That switch is the reason the
setup is split into [MAVLink bridge](mavlink-bridge.md) and
[Micro XRCE-DDS Agent](xrce-dds-agent.md) rather than one page.

## Hardware

The parts used in this demonstration. Substitute equivalents freely — see
[Scope](#scope).

| Item | Notes |
|---|---|
| Raspberry Pi Zero 2 W | 512 MB RAM, 2.4 GHz Wi-Fi only. Any Linux computer with a serial port works |
| Pixhawk 6C Mini | Any PX4 board with a spare telemetry port; TELEM2 is a 6-pin JST-GH connector |
| microSD card | 16 GB or larger, Class 10 |
| Custom TELEM2 harness | JST-GH to female jumper, hand-soldered — see [Serial connection](serial-connection.md) |
| 2×20 header pins | Soldered onto the Pi Zero 2 W, which ships unpopulated |
| micro-USB power supply | For bench work through the Pi's `PWR IN` port |

## Software versions

| Component | Version |
|---|---|
| Operating system | Ubuntu Server 22.04.5 LTS, 64-bit (arm64) |
| ROS 2 | Humble Hawksbill |
| PX4 | See [Micro XRCE-DDS Agent](xrce-dds-agent.md#confirming-the-px4-version) — must be v1.14 or later |
| Micro XRCE-DDS Agent | Built from source on the companion computer |
| Ground station | Ubuntu 22.04 + ROS 2 Humble |

ROS 2 Humble targets Ubuntu 22.04 specifically. Using a different Ubuntu release
means no `ros-humble-*` packages exist for it, so the Ubuntu version is not a free
choice.

## Scope

For this demonstration a Raspberry Pi Zero 2 W is used, but the companion computer
does not have to be one. Any Linux machine that can reach the flight controller over
a serial port will do — the ROS 2 install, the MAVLink test, the Micro XRCE-DDS
Agent, and the systemd service are all ordinary Linux and carry across unchanged.

Only two things are genuinely Raspberry Pi specific:

- [Flashing and first boot](pi-setup.md), which uses Raspberry Pi Imager
- [Enabling the UART](serial-connection.md#enabling-the-uart-on-the-pi), which edits
  the Pi's boot configuration

On another machine, skip those two and substitute your own serial device name
wherever `/dev/serial0` appears.

The same goes for the flight controller. A Pixhawk 6C Mini is used here, but any
board running PX4 v1.14 or later with a spare telemetry port works — check its pinout
against the [wiring table](serial-connection.md#pinout) before building the harness.

## Reference documentation

- [PX4: Raspberry Pi Companion with Pixhawk](https://docs.px4.io/main/en/companion_computer/pixhawk_rpi)
- [ArduPilot: ROS 2 on Raspberry Pi](https://ardupilot.org/dev/docs/ros2-pi.html)
- [ROS 2 Humble: Ubuntu install from Debian packages](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html)

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
