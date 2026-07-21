import typing
import subprocess
from time import sleep
from datetime import datetime
import os

from BarkNotificator import BarkNotificator

bark = BarkNotificator(device_token=os.environ["BARK_DEVICE_TOKEN"])


class TailscaleDevice:
    def __init__(self, ip: str, name: str, account: str, os: str, online: bool) -> None:
        self.ip = ip
        self.name = name
        self.account = account
        self.os = os
        self.online = online

    def __str__(self) -> str:
        return f"{self.name} ({self.ip}) {self.account} {self.os} {self.online}"


def get_tailscale_status() -> typing.List[TailscaleDevice]:
    process = subprocess.run(["tailscale", "status"], capture_output=True, text=True)
    if process.returncode != 0:
        raise Exception("Failed to get tailscale status")

    lines = process.stdout.split("\n")
    devices: typing.List[TailscaleDevice] = []
    for line in lines:
        if line.startswith("100."):
            parts = line.split()

            online = False
            status = parts[4]
            if not status.startswith("offline"):
                online = True

            ip = parts[0]
            name = parts[1]
            account = parts[2]
            os = parts[3]

            devices.append(TailscaleDevice(ip, name, account, os, online))

    return devices


def notify_online(device: TailscaleDevice) -> None:
    bark.send(
        title="Tailscale 设备上线",
        content=f"{device.name} ({device.ip}) 上线",
        category="tailscale",
        target_url="https://login.tailscale.com/admin/machines",
        icon_url="https://tailscale.com/favicon.png",
    )


def notify_offline(device: TailscaleDevice) -> None:
    bark.send(
        title="Tailscale 设备下线",
        content=f"{device.name} ({device.ip}) 下线",
        category="tailscale",
        target_url="https://login.tailscale.com/admin/machines",
        icon_url="https://tailscale.com/favicon.png",
    )


def main() -> None:
    last_seen = get_tailscale_status()

    while True:
        current_seen = get_tailscale_status()

        last_dict = {dev.ip: dev for dev in last_seen}
        curr_dict = {dev.ip: dev for dev in current_seen}

        all_ips = set(last_dict.keys()) | set(curr_dict.keys())

        for ip in all_ips:
            last_dev = last_dict.get(ip)
            curr_dev = curr_dict.get(ip)

            if curr_dev is None:
                if last_dev is not None:
                    notify_offline(last_dev)
            elif last_dev is None:
                if curr_dev.online:
                    notify_online(curr_dev)
                else:
                    notify_offline(curr_dev)
            else:
                if last_dev.online != curr_dev.online:
                    if curr_dev.online:
                        notify_online(curr_dev)
                    else:
                        notify_offline(curr_dev)

        last_seen = current_seen
        sleep(5)


if __name__ == "__main__":
    main()
