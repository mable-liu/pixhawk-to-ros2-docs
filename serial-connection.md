# Serial connection

Connect the Pixhawk's TELEM2 port to the Pi's UART pins. Everything else in this
guide runs over this cable, so get it right before moving on.

Two parts: making the cable, then setting up the Pi so the serial port works.

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

Notice that TX and RX cross over. Transmit on one board goes to receive on the other.
Connecting TX to TX is the most common mistake here, and it gives you no error at
all, just silence. If the [MAVLink test](mavlink-bridge.md) finds nothing, check this
first.

Ground is not optional. Serial needs a shared reference, so without pin 6 the link
fails even with TX and RX correct.

Do not connect +5V. The Pi draws more power than the TELEM port can supply, and
feeding 5V between two powered boards can damage both. Power the Pi separately, from
the micro-USB port on the bench or the drone's power supply in flight.

:::{admonition} Check the pinout for your own board
:class: warning
The table above follows the standard Pixhawk connector layout, which most modern
boards use. Older boards with DF13 connectors and some third-party boards do not.
Look up your board's pinout before cutting anything. A miswired cable can destroy the
flight controller.
:::

### Making the cable

No off-the-shelf cable fits both boards, so you make one:

1. Solder header pins onto the Pi. The Zero 2 W ships with empty holes.
2. Cut the telemetry cable that came with the Pixhawk, keeping the connector end.
3. Solder the three wires you need onto jumper wires that fit the Pi's pins.
4. Cover each joint with heat shrink so nothing shorts out under vibration.
5. Tuck the wires into the connector housing, then check continuity with a multimeter
   before powering anything on.

## Enabling the UART on the Pi

A fresh Ubuntu install will not give you a working serial port. Two things are in the
way, both fixed by editing the boot files.

**The login console is using it.** Linux sends login prompts down the same wires PX4
wants.

**Bluetooth has the better UART.** The Pi has two serial controllers. The good one
(`ttyAMA0`) is assigned to Bluetooth, leaving the weaker `ttyS0` on the GPIO pins,
and the weaker one is unreliable at the 921600 baud the
[agent](xrce-dds-agent.md) needs.

:::{note}
Pi specific. Same steps on the Pi 3 and Pi 4. The Pi 5 is laid out differently, so
check the Raspberry Pi docs for that board. On a non-Pi computer the serial port
usually works out of the box under a different name such as `/dev/ttyUSB0`, which you
then use everywhere this guide says `/dev/serial0`.
:::

### 1. Turn off the serial console

Open the kernel command line:

```bash
sudo nano /boot/firmware/cmdline.txt
```

Delete `console=serial0,115200` and leave the rest of the line alone. The whole file
is a single line, so do not press enter.

Then stop the login service from claiming the port. Disable both, since which one is
in use depends on settings you are about to change:

```bash
sudo systemctl disable --now serial-getty@ttyS0.service
sudo systemctl disable --now serial-getty@ttyAMA0.service
```

### 2. Turn on the UART and free up ttyAMA0

Open the boot config:

```bash
sudo nano /boot/firmware/config.txt
```

Add these two lines at the end:

```ini
enable_uart=1
dtoverlay=disable-bt
```

`enable_uart=1` switches the serial port on. `dtoverlay=disable-bt` moves the good
UART off Bluetooth and onto the GPIO pins, so `/dev/serial0` points to `ttyAMA0`
instead of `ttyS0`. You lose Bluetooth, which does not matter here.

Also stop the service that talks to the Bluetooth chip:

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

The boot files need a reboot and the group change needs a fresh login. Once you are
back:

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
