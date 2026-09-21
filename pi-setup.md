# Raspberry Pi setup

Flash the SD card and get an SSH connection to the Pi.

The SD card holds the operating system. We use Ubuntu Server instead of Raspberry Pi
OS because ROS 2 Humble is only packaged for Ubuntu 22.04.

## Flash the SD card

Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) on your laptop.

1. **Choose Device**: Raspberry Pi Zero 2 W
2. **Choose OS**: `Other general-purpose OS` → `Ubuntu` →
   **Ubuntu Server 22.04.5 LTS (64-bit)**
3. **Choose Storage**: your SD card

Pick the 64-bit version. ROS 2 Humble is only packaged for 64-bit, and the 32-bit
image will leave you stuck at the install step.

## Set up Wi-Fi and SSH

Before writing, open the settings (the gear icon, or **Edit Settings** when Imager
asks if you want to customise the OS):

| Setting | Value |
|---|---|
| Hostname | `ubuntu` |
| Enable SSH | Yes, with password authentication |
| Username | `ubuntu` |
| Password | Your choice |
| Wireless LAN SSID | Your 2.4 GHz network |
| Wireless LAN password | Your network password |
| Wireless LAN country | Your two-letter country code |
| Locale / timezone | Your settings |

The hostname becomes the address you SSH to (`ubuntu.local`) and the username becomes
the account you log in as. If you pick different values, use yours instead of
`ubuntu` everywhere below.

:::{important}
The Pi Zero 2 W only has a 2.4 GHz radio. It cannot see 5 GHz networks. If your router
uses one name for both bands, check that the Pi is allowed on 2.4 GHz, or it will
flash fine and then never appear on the network.
:::

Write the image, then put the card in the Pi.

## First boot

1. Plug power into the **`PWR IN`** micro-USB port, the one further from the
   mini-HDMI socket. The other port is for data and will not power the board
   properly. Both are labelled on the underside.

2. Wait a minute or two. The first boot takes longer than usual because Ubuntu
   resizes the filesystem and runs its setup scripts.

3. Connect your laptop to the same Wi-Fi network, then SSH in:

   ```bash
   ssh ubuntu@ubuntu.local
   ```

   Use the password you set in Imager.

### If `ubuntu.local` does not resolve

Some networks block the protocol behind `.local` names. Find the Pi's IP address
instead, either from your router's device list or by scanning:

```bash
arp -a
```

Then connect to that address:

```bash
ssh ubuntu@<pi-ip-address>
```

## Shutting down

To close the SSH session:

```bash
exit
```

Always shut down before unplugging the Pi. Cutting power to a running Pi can corrupt
the SD card:

```bash
sudo shutdown now
```

The SSH connection will drop, which is normal. Wait for the green LED to stop
flashing before removing power.

## Next

[Install ROS 2](ros2-install.md)
