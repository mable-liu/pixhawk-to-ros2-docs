# Serial connection

Connecting the Pixhawk's TELEM2 port to the Raspberry Pi's UART pins, so the two
boards can talk over a serial link. This is the physical foundation for everything
in the rest of this document — both the [MAVLink bridge](mavlink-bridge.md) and the
[Micro XRCE-DDS Agent](xrce-dds-agent.md) run over this one link.

There are two halves: building the wiring harness, and configuring the Pi's UART so
that `/dev/serial0` is actually usable.

## Wiring

```{image} _static/images/telem2-pi-wiring-harness.png
:alt: Wiring diagram showing the Pi Zero 2 W GPIO header connected to the flight controller TELEM port, with TX and RX crossed over and the +5V line unused
:width: 520px
:align: center
```

### Pinout

The Pixhawk's TELEM2 is a 6-pin JST-GH connector following the Pixhawk connector
standard. Only three of its six conductors are used:

| TELEM2 pin | Signal | Raspberry Pi pin | Pi signal |
|---|---|---|---|
| 1 | VCC (+5V) | — | **Not connected** |
| 2 | TX | Pin 10 | RXD (GPIO 15) |
| 3 | RX | Pin 8 | TXD (GPIO 14) |
| 4 | CTS | — | Not connected |
| 5 | RTS | — | Not connected |
| 6 | GND | Pin 6 | GND |

Three things to get right:

**TX and RX cross over.** The Pixhawk's transmit line goes to the Pi's receive line
and vice versa. Wiring TX to TX is the most common failure here, and it fails
silently — no error, just no data. If nothing arrives during
[MAVLink testing](mavlink-bridge.md), check this first.

**Ground is mandatory.** Serial signalling is referenced to a shared ground. Without
pin 6 connected, the link will not work even with TX and RX correct.

**Leave +5V disconnected.** The Pi Zero 2 W draws more current than the TELEM port is
meant to supply, and back-feeding 5 V between two independently powered boards risks
damaging both. Power the Pi from its own supply — the `PWR IN` micro-USB port on the
bench, or the drone's power distribution in flight. CTS and RTS are unused because
hardware flow control is not enabled on this link.

:::{admonition} Confirm the connector on your board
:class: warning
The pin numbering above is the Pixhawk connector standard as documented by PX4. The
Pixhawk 6C Mini's specific TELEM2 pinout was not re-checked against the Holybro
pinout sheet for this document. Verify against the silkscreen or Holybro's
documentation before cutting the cable — a miswired harness can damage the flight
controller.
:::

### Building the harness

The Pi has no connector that matches the Pixhawk telemetry cable, so a harness is
made by hand:

1. Solder header pins onto the Pi Zero 2 W. The board ships with an unpopulated
   2×20 header footprint, so the UART pins have nothing to connect to until this is
   done.
2. Cut the JST-GH telemetry cable that came with the Pixhawk, keeping the connector
   end intact.
3. Solder the three needed conductors to wires terminating in female jumper
   connectors that fit the Pi's header pins.
4. Sleeve each solder joint in heat-shrink tubing for insulation, so adjacent joints
   cannot short against each other under vibration.
5. Seat the wires in the connector housing and check continuity with a multimeter
   before powering anything.

## Enabling the UART on the Pi

A fresh Ubuntu Server image does not give you a usable `/dev/serial0`. Two things
are in the way:

- **A serial console** is attached to the UART, so Linux is transmitting login
  prompts down the same wires PX4 wants to use.
- **Bluetooth owns the good UART.** The Pi has two: the PL011 (`ttyAMA0`), which is
  full-featured and stable, and the mini-UART (`ttyS0`), whose baud rate is derived
  from the variable VPU core clock. By default the PL011 is assigned to Bluetooth
  and the mini-UART is on the GPIO pins. At 921600 baud — the rate the
  [XRCE-DDS agent](xrce-dds-agent.md) needs — the mini-UART is not reliable.

Both are fixed by editing the boot configuration.

:::{admonition} Reconstructed from upstream documentation
:class: warning
The original notes went straight to `/dev/serial0` without recording this step. The
configuration below follows the PX4 companion computer guide. The exact contents of
the lab Pi's `/boot/firmware/config.txt` and `/boot/firmware/cmdline.txt` have not
been read back, so confirm these match what is actually running.
:::

### 1. Disable the serial console

On Ubuntu Server for Raspberry Pi, edit `/boot/firmware/cmdline.txt` and remove the
`console=serial0,115200` entry, leaving the rest of the line untouched. The file is
a single line — do not add line breaks.

```bash
sudo nano /boot/firmware/cmdline.txt
```

Then stop the login prompt service from reclaiming the port:

```bash
sudo systemctl disable --now serial-getty@ttyAMA0.service
```

### 2. Enable the UART and free the PL011

Append to `/boot/firmware/config.txt`:

```ini
enable_uart=1
dtoverlay=disable-bt
```

```bash
sudo nano /boot/firmware/config.txt
```

`enable_uart=1` turns on the UART on the GPIO header. `dtoverlay=disable-bt` releases
the PL011 from Bluetooth and moves it onto GPIO 14/15, so `/dev/serial0` becomes a
symlink to `ttyAMA0` instead of `ttyS0`. Bluetooth is unavailable afterwards, which
is fine for a flight computer.

Also disable the service that initialises the Bluetooth modem over that UART:

```bash
sudo systemctl disable hciuart
```

### 3. Grant serial access to your user

Serial devices are owned by the `dialout` group. Without membership, every command in
the following pages needs `sudo`:

```bash
sudo usermod -aG dialout $USER
```

### 4. Reboot and verify

```bash
sudo reboot
```

Group membership only takes effect on a new login, and the boot configuration
changes need the reboot regardless. Once back in:

```bash
ls -l /dev/serial0
```

Expected: a symlink pointing at `ttyAMA0`.

```text
lrwxrwxrwx 1 root root 7 Aug  4 22:10 /dev/serial0 -> ttyAMA0
```

If it points at `ttyS0`, the `disable-bt` overlay did not take effect — recheck
`config.txt` and reboot again.

Confirm your group membership too:

```bash
groups
```

Expected: `dialout` appears in the list.

## Next

Prove the link carries data → [MAVLink bridge](mavlink-bridge.md)
