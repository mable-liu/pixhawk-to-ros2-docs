# Raspberry Pi setup

Flashing the microSD card and getting a headless SSH session onto the Pi.

The microSD card is the Pi's only storage — it holds the operating system the Pi
boots from. The stock Raspberry Pi OS is replaced with Ubuntu Server, because ROS 2
Humble is packaged for Ubuntu 22.04 and not for Raspberry Pi OS.

## Flashing the microSD card

Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) on your laptop.

1. **Choose Device** — Raspberry Pi Zero 2 W.
2. **Choose OS** — `Other general-purpose OS` → `Ubuntu` →
   **Ubuntu Server 22.04.5 LTS (64-bit)**.
3. **Choose Storage** — the microSD card.

The 64-bit build matters. The Pi Zero 2 W has a 64-bit CPU, and the `ros-humble-*`
packages are published for `arm64`. Flashing the 32-bit `armhf` image leaves you with
no installable ROS 2 packages later.

## Configuring Wi-Fi and SSH during flashing

Before writing, open the settings dialog (the gear icon, or **Edit Settings** when
Imager offers to customise the OS) and set:

| Setting | Value |
|---|---|
| Hostname | `ubuntu` |
| Enable SSH | Yes, *Use password authentication* |
| Username | `ubuntu` |
| Password | *(see below)* |
| Wireless LAN SSID | Your lab's 2.4 GHz network |
| Wireless LAN password | The network password |
| Wireless LAN country | Your two-letter country code |
| Locale / timezone | Your local settings |

These are what make the rest of this document work. The hostname sets what you SSH
to (`ubuntu.local`), and the username sets who you SSH as. If you choose different
values, substitute them everywhere below.

:::{admonition} Wi-Fi credentials
:class: important
The Pi Zero 2 W has a 2.4 GHz radio only — it cannot see a 5 GHz network. If your
lab AP broadcasts one SSID on both bands with band steering, confirm the Pi is
allowed to associate on 2.4 GHz, or the Pi will flash successfully and then never
appear on the network.

Set the account password to your lab's Pi password. It is deliberately not recorded
in this document, since this page is published publicly.
:::

Write the image, then move the card to the Pi.

## First boot and SSH

1. Power the Pi through the **`PWR IN`** micro-USB port — the one closer to the
   corner of the board. The other micro-USB port is `USB` (data) and will not power
   the board reliably.

   :::{tip}
   The Pi Zero 2 W has two identical-looking micro-USB ports. They are labelled on
   the underside of the board.
   :::

2. Wait for first boot. Ubuntu Server expands the filesystem and runs cloud-init on
   the first boot, so it can be a minute or two before SSH answers — longer than a
   steady-state boot.

3. Connect your laptop to the **same Wi-Fi network** you configured in Imager, then
   SSH in:

   ```bash
   ssh ubuntu@ubuntu.local
   ```

   Enter the password you set during flashing.

### If `ubuntu.local` does not resolve

That hostname is resolved by mDNS, which some networks block and some client
configurations do not support. If it fails, find the Pi's IP address instead — check
the connected-clients list on the lab router, or scan from your laptop:

```bash
# macOS / Linux — look for a Raspberry Pi Foundation MAC address
arp -a
```

Then connect by address:

```bash
ssh ubuntu@<pi-ip-address>
```

## Ending a session safely

To close the SSH connection and return to your laptop's shell:

```bash
exit
```

Before unplugging the Pi, shut it down properly. Pulling power from a running Pi
risks corrupting the SD card filesystem:

```bash
sudo shutdown now
```

The SSH connection drops as the Pi halts, which is expected. Wait for the green
activity LED to stop flickering before removing power.

## Next

Install ROS 2 → [ROS 2 installation](ros2-install.md)
