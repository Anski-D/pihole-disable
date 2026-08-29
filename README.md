# Pihole-Disable

![GitHub Release](https://img.shields.io/github/v/release/Anski-D/pihole-disable)
![GitHub License](https://img.shields.io/github/license/Anski-D/pihole-disable)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FAnski-D%2Fpihole-disable%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

A simple-to-use web interface for temporarily disabling a local Pi-hole network DNS blocker.

Main features:
* Time-limited disabling of blocking either:
  * Network-wide;
  * Per device (based on LAN IP).
* Uses existing Pi-hole API.
* Runs entirely within the local network.

## Introduction

### What is a Pi-hole?

If you are still reading, you probably already know, but for the uninitiated...

A Pi-hole is a program that runs on your local network that is configured to filter the DNS queries your devices make. If the query matches a pattern on the enabled blocklist, it gets thrown away. In this way, a Pi-hole can be used to block unwanted content, such as adverts, by blocking certain domains.

DNS blocking stops the blocked content from ever being received, because it is never requested.

### What does `pihole-disable` do?

Sometimes the Pi-hole blocks websites or elements of them that you do not want blocked. This can be overcome by disabling the Pi-hole temporarily (or altering the blocklist), _if_ you have the administrative access to do that.

In a household where the less technically inclined might need to do this, `pihole-disable` provides an accessible way of doing this.

### What `pihole-disable` can do

The app can be used to temporarily disable the Pi-hole for either the whole network or the local device.

### What `pihole-disable` cannot do (and other limitations)

The app cannot be used to update the blocklist.

It should not be used on home networks where you wish to prevent people from accessing certain content by means of Pi-hole DNS blocking (e.g., prevent children accessing adult content), because it is _specifically made to make circumventing this easy._

It should not be used on networks where you want zero risk of someone potentially altering your Pi-hole configuration. Due to the app needing Pi-hole API access to work, those with knowledge of the API could exploit it to make changes.

## Prerequisites

1. [A working instance of Pi-hole.](https://pi-hole.net/)
1. A working Python installation.
1. Basic knowledge in how to run a web server on a local device and access it on your local network (beyond the scope of this guide).
2. (Optional) A working Docker installation.

## Installation

Take a clone of this repo then change to the new directory:

```shell
git clone https://github.com/Anski-D/pihole-disable.git
cd pihole-disable
```

`pihole-disable` uses the Pi-hole API. A `.env` file is required by `pihole-disable` to access that API.

An app password is needed to access the API. This can be done from the web interface by going to `Settings > Web interface / API`, ensure the settings toggle in the top-right is switched from 'Basic' to 'Expert', and then doing the 'Configure app password' process.

The URL to the API is also required. In a default Pi-hole installation this should `https://pi.hole/api` or if using the Pi-hole device's IP address `https://<IP_ADDRESS>/api`.

These two pieces of information should be added to the `.env` files as follows:

```shell filename=".env"
API_PASSWORD=<API_PASSWORD>
API_URL=<API_URL>
```

Then to be on the safe side, remove all but the most necessary permissions from the file to prevent unwanted snooping:
```shell
chmod 600 .env
```

## Usage

How to run the app is ultimately up to the user, but example configuration is provided for both Docker and running Python via a shell script.

### Docker

The required configuration files for running in Docker is provided. There is a `Dockerfile` to build the image, and an example `compose.yaml` (`compose.yaml.example`) can be copied to run the container.

The `Dockerfile` should not need any changes. The example `compose.yaml` can be modified as required (e.g., changing which port to bind), and includes some commented lines for including logging in a Docker volume (if persistent logs are desired).

To then build the image and run the container:

```shell
docker compose up --build -d
```

Alternatively, the build and running can be defined at the command line.

Top shutdown the container, run in the same directory as the `compose.yaml` file:

```shell
docker compose down
```

### Python (via shell)

The use of a Python virtual environment is highly recommended. With the virtual environment activated, run:

```shell
pip install .
```

This installs `pihole-disable` and the required dependencies (including the webserver package, `hypercorn`).

There are three helper scripts provided, `run_pihole-disable.sh`, `stop_pihole-disable.sh`, and `restart_pihole-disable.sh`, which respectively run, stop, and restart `pihole-disable`. These are not mandatory, but should be used as a reference for how to run the app. There are some lines at the top of the `run_pihole-disable.sh` script that can be modified as necessary.

Alternatively, the app can be launched directly from the command line or a custom launch script used.

## Uninstallation

To remove `pihole-disable` simply stop the app running then delete the directory cloned during the installation step. For Docker installations, feel free to also delete any remaining images and volumes.
