# Micro XRCE-DDS Agent

The Micro XRCE-DDS Agent is the bridge between PX4 and ROS 2. PX4 runs a
`uxrce_dds_client` that publishes its internal uORB messages down the serial link;
the agent runs on the Pi, receives them, and republishes them onto the DDS network
as ROS 2 topics. It translates in both directions, so ROS 2 nodes can also publish
commands back into PX4.

This replaces the [MAVLink](mavlink-bridge.md) configuration on TELEM2.

## Confirming the PX4 version

The `uxrce_dds_client` module exists in **PX4 v1.14 and later**. On older firmware,
none of this page applies.

Check the version from QGroundControl's **Analyze → MAVLink Console**:

```bash
ver all
```

:::{important}
Write the version down before moving on. It determines which branch of `px4_msgs` you
need in [Ground station](ground-station.md), and a mismatch there causes a failure
that is hard to diagnose after the fact.
:::

## PX4 parameters for uXRCE-DDS

In QGroundControl over USB, go to **Vehicle Setup → Parameters** and change:

| Parameter | Value | Meaning |
|---|---|---|
| `MAV_1_CONFIG` | `0` (Disabled) | Release TELEM2 from MAVLink |
| `UXRCE_DDS_CFG` | `102` (TELEM2) | Run the DDS client on TELEM2 |
| `SER_TEL2_BAUD` | `921600` | Raise the serial rate |

The baud rate goes up from 57600 because the DDS client carries far more data than a
MAVLink telemetry stream — full-rate uORB topics rather than a summary feed.

:::{admonition} Reboot the flight controller
:class: important
As on the previous page, the port assignment is read at boot. Reboot before testing.
:::

The higher baud rate is also why `dtoverlay=disable-bt` was set in
[Serial connection](serial-connection.md#2-enable-the-uart-and-free-the-pl011). The
mini-UART's clock is not stable enough for reliable 921600 baud; the PL011 is.

## Building the agent

The agent is not packaged for Ubuntu, so it is built from source on the Pi.

```bash
sudo apt install cmake git

git clone https://github.com/eProsima/Micro-XRCE-DDS-Agent.git
cd Micro-XRCE-DDS-Agent
mkdir build && cd build
cmake ..
make
sudo make install
sudo ldconfig /usr/local/lib/
```

:::{admonition} 512 MB of RAM is not much
:class: important
This is the step most likely to fail on a Pi Zero 2 W. A parallel build
(`make -j4`) will exhaust memory and the kernel's OOM killer will terminate the
compiler — which surfaces as a confusing `c++: fatal error: Killed signal terminated
program cc1plus` rather than an out-of-memory message.

Build single-threaded with plain `make`, and if it still fails, add swap first:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

That swap file does not survive a reboot. Since it is only needed for this one build,
that is usually fine — remove it afterwards with `sudo swapoff /swapfile && sudo rm
/swapfile` to avoid wearing the SD card.

Expect the build to take a long time regardless.
:::

Confirm the binary is installed and on your path:

```bash
which MicroXRCEAgent
```

Expected: `/usr/local/bin/MicroXRCEAgent`

## Testing the bridge

### 1. Check the PX4 side

In QGroundControl's **MAVLink console**:

```bash
uxrce_dds_client status
```

Expected:

```text
Running, connected
transport: serial
```

If it reports running but not connected, PX4 is transmitting but the agent is not
answering — start the agent and check again.

### 2. Start the agent on the Pi

In the SSH session, leave this running:

```bash
MicroXRCEAgent serial --dev /dev/serial0 -b 921600
```

Expected: log lines showing a session established, then a series of
`create_datawriter` / `create_topic` entries as PX4 registers each uORB topic.

```text
[1754353821.123456] info     | TermiosAgentLinux.cpp | init                     | running...             | fd: 3
[1754353822.456789] info     | Root.cpp           | create_client            | create                 | client_key: 0x00000001
[1754353822.567890] info     | SessionManager.hpp | establish_session        | session established    | client_key: 0x00000001
```

If you have not added yourself to the `dialout` group, this needs `sudo`. See
[Serial connection](serial-connection.md#3-grant-serial-access-to-your-user).

### 3. List the topics

Open a **second** SSH session to the Pi, leaving the agent running in the first:

```bash
source /opt/ros/humble/setup.bash
ros2 topic list
```

If the bridge is working, the PX4 topics appear:

```text
/fmu/in/offboard_control_mode
/fmu/in/trajectory_setpoint
/fmu/in/vehicle_command
/fmu/out/failsafe_flags
/fmu/out/sensor_combined
/fmu/out/timesync_status
/fmu/out/vehicle_attitude
/fmu/out/vehicle_status
/parameter_events
/rosout
```

Topics under `/fmu/out/` are published by PX4; `/fmu/in/` are the ones PX4 subscribes
to for commands.

Seeing only `/parameter_events` and `/rosout` means the agent is running but no PX4
client is attached — go back to step 1.

Press {kbd}`Ctrl` + {kbd}`C` to stop the agent.

## Next

Having to start the agent by hand after every boot is impractical on a drone. Set it
to start automatically → [Autostart](autostart.md)

To read the topics from another machine → [Ground station](ground-station.md)
