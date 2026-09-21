# MAVLink bridge

Before setting up ROS 2, check that the Pi and the Pixhawk can talk to each other.
MAVProxy is a small ground station that runs in the terminal. If it sees a heartbeat
from the flight controller, then your wiring, your serial setup, and your PX4
settings are all correct.

This is only a test. Once it passes you switch the port over to uXRCE-DDS on
[the next page](xrce-dds-agent.md).

## Connect QGroundControl

You set the PX4 parameters below from QGroundControl, which needs its own connection
to the flight controller. Plug the Pixhawk into your laptop over **USB**.

:::{important}
Do not use a TELEM2 telemetry radio for this. You are about to disable MAVLink on
TELEM2, which would disconnect QGroundControl and leave you unable to undo it without
a USB cable.
:::

## PX4 settings

In QGroundControl, go to **Vehicle Setup → Parameters** and set:

| Parameter | Value | What it does |
|---|---|---|
| `MAV_1_CONFIG` | `TELEM2` | Runs MAVLink on TELEM2 |
| `UXRCE_DDS_CFG` | `0` (Disabled) | Keeps the DDS client off that port |
| `SER_TEL2_BAUD` | `57600` | Sets the speed of the link |

Only one protocol can use a serial port at a time, so turning on MAVLink means
turning off uXRCE-DDS.

:::{important}
Reboot the flight controller after changing these. PX4 only reads the port settings
at startup, so nothing happens until you restart it. QGroundControl will offer to
reboot for you.
:::

## Install MAVProxy on the Pi

In your SSH session:

```bash
sudo apt install python3-pip
sudo pip3 install mavproxy
sudo apt remove modemmanager
```

Remove ModemManager. It checks new serial devices to see if they are cellular modems,
and while doing that it sends data down the link and breaks the connection. It looks
exactly like a wiring fault.

The install takes a few minutes on a Pi Zero 2 W.

## Test the connection

Power up the Pixhawk with TELEM2 connected to the Pi, then run:

```bash
mavproxy.py --master=/dev/serial0 --baudrate 57600
```

You should see something like this:

```text
Connect /dev/serial0 source_system=255
Log Directory:
Telemetry log: mav.tlog
Waiting for heartbeat from /dev/serial0
MAV> Detected vehicle 1:1 on link 0
online system 1
```

Once `Detected vehicle` appears, the cable works.

If it sits on `Waiting for heartbeat` forever, nothing is coming through. See
[Troubleshooting](troubleshooting.md#no-mavlink-heartbeat).

Press {kbd}`Ctrl` + {kbd}`C` to quit.

## Next

[Set up the Micro XRCE-DDS Agent](xrce-dds-agent.md)
