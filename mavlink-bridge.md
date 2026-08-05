# MAVLink bridge

Before configuring ROS 2, prove that the Pi and the Pixhawk can actually talk over
the [serial link](serial-connection.md). MAVProxy is a lightweight MAVLink ground
station that runs in a terminal — if it shows a heartbeat, the wiring, the UART
configuration, and the PX4 port settings are all correct.

This is a diagnostic step. Once it passes, TELEM2 is reconfigured for uXRCE-DDS in
[the next section](xrce-dds-agent.md) and MAVLink is switched back off.

## Connecting QGroundControl

The PX4 parameters below are set from QGroundControl, which needs its own link to
the flight controller. Connect the Pixhawk to your laptop over **USB** — not over
TELEM2, which is about to be reconfigured out from under you.

:::{admonition} Do not configure TELEM2 over TELEM2
:class: important
If your only link to the flight controller is the telemetry radio on TELEM2, setting
`MAV_1_CONFIG = 0` later will disconnect QGroundControl and leave you unable to
change it back without a USB cable. Use USB for all parameter changes.
:::

## PX4 parameters for MAVLink

In QGroundControl, go to **Vehicle Setup → Parameters** and set:

| Parameter | Value | Meaning |
|---|---|---|
| `MAV_1_CONFIG` | `TELEM2` | Run a MAVLink instance on TELEM2 |
| `UXRCE_DDS_CFG` | `0` (Disabled) | Keep the DDS client off this port |
| `SER_TEL2_BAUD` | `57600` | Serial rate for TELEM2 |

`MAV_1_CONFIG` and `UXRCE_DDS_CFG` both claim a serial port, and two protocols cannot
share one UART. Setting one requires disabling the other.

:::{admonition} Reboot after changing these
:class: important
`MAV_1_CONFIG` and `UXRCE_DDS_CFG` only take effect after the flight controller
restarts — the port assignment is read at boot. QGroundControl prompts for a reboot
when a parameter requires one; take it. Without the reboot the port stays as it was
and the test below fails for reasons that have nothing to do with your wiring.
:::

## Installing MAVProxy on the Pi

In the SSH session on the Pi:

```bash
sudo apt install python3-pip
sudo pip3 install mavproxy
sudo apt remove modemmanager
```

Removing ModemManager matters. It probes newly appeared serial devices looking for
cellular modems, and in doing so it grabs `/dev/serial0` and injects bytes into the
link — which corrupts MAVLink framing in a way that looks like a wiring fault.

:::{admonition} Reconstructed from upstream documentation
:class: warning
The original notes recorded only that "MAVProxy was installed". These commands come
from the PX4 companion computer guide. Expect the `pip3 install` to be slow on a Pi
Zero 2 W.
:::

## Testing the link

With the Pixhawk powered and TELEM2 wired to the Pi:

```bash
mavproxy.py --master=/dev/serial0 --baudrate 57600
```

Expected: MAVProxy connects and reports a heartbeat from the flight controller,
followed by a stream of status messages and a `MAV>` prompt.

```text
Connect /dev/serial0 source_system=255
Log Directory:
Telemetry log: mav.tlog
Waiting for heartbeat from /dev/serial0
MAV> Detected vehicle 1:1 on link 0
online system 1
```

Once you see `Detected vehicle`, the serial path is proven end to end.

If it sits on `Waiting for heartbeat` indefinitely, nothing is arriving. Work through
[Troubleshooting → No heartbeat](troubleshooting.md#no-mavlink-heartbeat).

Press {kbd}`Ctrl` + {kbd}`C` to exit MAVProxy.

## Next

Switch the port to uXRCE-DDS → [Micro XRCE-DDS Agent](xrce-dds-agent.md)
