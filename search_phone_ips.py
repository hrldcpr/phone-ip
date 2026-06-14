#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "linode_api4",
#     "twilio",
# ]
# ///

import ipaddress
import os
import sys
import time

import linode_api4
import twilio.rest

import data
import secret

ALREADY_MINE = {2892553077, 3038809599}
REGIONS = {"us-east", "us-central", "eu-central"}
TYPE = "g6-nanode-1"
BATCH = 32  # number of simultaneous linodes
N = 4  # number of rounds
SEEN_IPS_FILE = "seen_ips.txt"

sys.stdout.reconfigure(line_buffering=True)

linode_client = linode_api4.LinodeClient(secret.LINODE_PERSONAL_ACCESS_TOKEN)
twilio_client = twilio.rest.Client(secret.TWILIO_SID, secret.TWILIO_CLIENT_SECRET)


def run_batch(region, seen_ips):
    linodes = []
    seen_count = 0
    try:
        for i in range(BATCH):
            linode = linode_client.linode.instance_create(
                ltype=TYPE, region=region, booted=False
            )
            linodes.append(linode)

            ip_str = linode.ipv4[0]
            ip = int(ipaddress.ip_address(ip_str))

            seen = ip_str in seen_ips
            if seen:
                seen_count += 1

            print(
                f"{region} {i:02d}/{BATCH} {ip_str} = {ip:010d} {'seen' if seen else 'new'} ({100 * seen_count // len(linodes)}% seen)"
            )

            if ip >= 200_000_0000:
                area_code = int(str(ip)[:3])
                country_code = data.AREA_CODE_COUNTRY_CODES.get(area_code, "US")

                numbers = twilio_client.available_phone_numbers(
                    country_code
                ).local.list(contains=str(ip), sms_enabled=True)
                print(numbers)

                if numbers or ip in ALREADY_MINE:
                    print(f"XXX FOUND {ip} XXX")
                    linodes.pop()  # remove from deletion list
                    twilio_client.incoming_phone_numbers.create(
                        phone_number=numbers[0].phone_number
                    )
                    raise Exception("XXX FOUND XXX")

            seen_ips.add(ip_str)
            time.sleep(0.1)

    finally:
        for linode in linodes:
            try:
                print(f"delete {linode.ipv4[0]}")
                linode.delete()
                time.sleep(0.1)
            except Exception as e:
                print(e)


def main():
    seen_ips = set()
    with open(SEEN_IPS_FILE) as f:
        for line in f:
            seen_ips.add(line.strip())

    try:
        for _ in range(N):
            for region in REGIONS:
                run_batch(region, seen_ips)

    finally:
        with open(SEEN_IPS_FILE + ".tmp", "w") as f:
            for ip in sorted(seen_ips):
                print(ip, file=f)
        os.rename(SEEN_IPS_FILE + ".tmp", SEEN_IPS_FILE)


main()
