# Serial connection

Connect the Pixhawk's TELEM2 port to the Pi's UART pins. Everything else in this
guide runs over this cable, so get it right before moving on.

There are two parts: making the cable, and setting up the Pi so the serial port
works.

## Wiring

```{image} _static/images/telem2-pi-wiring-harness.png
:alt: Wiring diagram showing the Pi Zero 2 W GPIO header connected to the flight controller TELEM port, with TX and RX crossed over and the +5V line unused
:width: 520px
:align: center
```

### Pinout

TELEM2 is a 6-pin JST-GH connector. You only need three of the six wires:

| TELEM2 pin | Signal | Pi pin | Pi signal |
|---|---|---|---|
| 1 | VCC (+5V) | — | **Do not connect** |
| 2 | TX | Pin 10 | RXD (GPIO 15) |
| 3 | RX | Pin 8 | TXD (GPIO 14) |
| 4 | CTS | — | Not used |
| 5 | RTS | — | Not used |
| 6 | GND | Pin 6 | GND |

Three things to watch for.

**TX goes to RX.** The Pixhawk's transmit wire connects to the Pi's receive pin, and
the other way around. Connecting TX to TX is the most common mistake, and it gives no
error at all, just no data. If nothing works during the
[MAVLink test](mavlink-bridge.md), check this first.

**Connect the ground.** Serial needs a shared ground to work. Without pin 6 the link
will fail even if TX and RX are correct.

**Leave +5V unconnected.** The Pi draws more power than the TELEM port can supply,
and feeding 5V between two powered boards can damage both. Power the Pi separately,
from the micro-USB port on the bench or the drone's power supply in flight. CTS and
RTS are unused because this link does not use hardware flow control.

:::{admonition} Check the pinout for your own board
:class: warning
The table above follows the standard Pixhawk connector layout, which most modern
boards use. Older boards with DF13 connectors and some third-party boards do not.
Look up your board's pinout before cutting anything. A miswired cable can destroy the
flight controller.
:::

### Making the cable

The Pi has no connector that fits the Pixhawk telemetry cable, so you make one:

1. Solder header pins onto the Pi. The Zero 2 W ships with empty header holes, so
   there is nothing to plug into until you do.
2. Cut the telemetry cable that came with the Pixhawk, keeping the connector end.
3. Solder the three wires you need onto jumper wires that fit the Pi's pins.
4. Cover each joint with heat shrink so nothing shorts out from vibration.
5. Tuck the wires into the connector housing and check continuity with a multimeter
   before powering anything on.

## Enabling the UART on the Pi

A fresh Ubuntu install will not give you a working serial port. Two things get in the
way:

- **The login console uses it.** Linux sends login prompts down the same wires PX4
  wants to use.
- **Bluetooth has the better UART.** The Pi has two serial controllers. The good one
  (`ttyAMA0`) is assigned to Bluetooth, leaving the weaker one (`ttyS0`) on the GPIO
  pins. The weaker one is not reliable at 921600 baud, which is what the
  [agent](xrce-dds-agent.md) needs.

Both are fixed by editing two boot files.

:::{note}
This section is Raspberry Pi specific. The steps are the same on the Pi 3 and Pi 4.
The Pi 5 is laid out differently, so check the Raspberry Pi documentation for that
board. On a non-Pi computer the serial port usually works out of the box, though it
will have a different name such as `/dev/ttyUSB0`. Use that name wherever this guide
says `/dev/serial0`.
:::

### 1. Turn off the serial console

Open `/boot/firmware/cmdline.txt` and delete `console=serial0,115200`. Leave the rest
of the line alone. It is all one line, so do not press enter.

```bash
sudo nano /boot/firmware/cmdline.txt
```

Then stop the login service from taking the port back:

```bash
sudo systemctl disable --now serial-getty@ttyAMA0.service
```

### 2. Turn on the UART and free up ttyAMA0

Add these two lines to the end of `/boot/firmware/config.txt`:

```ini
enable_uart=1
dtoverlay=disable-bt
```

```bash
sudo nano /boot/firmware/config.txt
```

`enable_uart=1` switches on the serial port. `dtoverlay=disable-bt` takes the good
UART away from Bluetooth and puts it on the GPIO pins, so `/dev/serial0` points to
`ttyAMA0` instead of `ttyS0`. You lose Bluetooth, which does not matter here.

Also turn off the service that talks to the Bluetooth chip:

```bash
sudo systemctl disable hciuart
```

### 3. Give your user access to the serial port

Serial ports belong to the `dialout` group. Without it, every command on the
following pages needs `sudo`:

```bash
sudo usermod -aG dialout $USER
```

### 4. Reboot and check

```bash
sudo reboot
```

The boot files need a reboot, and group changes only apply after you log in again.
Once you are back:

```bash
ls -l /dev/serial0
```

It should point to `ttyAMA0`:

```text
lrwxrwxrwx 1 root root 7 Aug  4 22:10 /dev/serial0 -> ttyAMA0
```

If it points to `ttyS0` instead, the `disable-bt` line did not take effect. Check
`config.txt` and reboot again.

Check your groups too:

```bash
groups
```

`dialout` should be in the list.

## Next

[Test the link with MAVLink](mavlink-bridge.md)
