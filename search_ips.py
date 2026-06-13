#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#     "linode_api4",
# ]
# ///

import ipaddress
import os
import time
from linode_api4 import LinodeClient

import secret

REGION = "eu-central"
TYPE = "g6-nanode-1"
BATCH_SIZE = 8


def explore_ip_batch():
    print("Initializing Linode client...")
    client = LinodeClient(secret.LINODE_PERSONAL_ACCESS_TOKEN)

    # We store them in a list so we can delete them all later
    created_linodes = []

    try:
        print(f"Requesting {BATCH_SIZE} instances in {REGION}...")

        # 1. Create multiple instances to grab different IPs
        for i in range(BATCH_SIZE):
            print(f"  Creating Linode {i+1}/{BATCH_SIZE}...")
            new_linode = client.linode.instance_create(
                ltype=TYPE, region=REGION, booted=False
            )
            created_linodes.append(new_linode)

            ip_address = new_linode.ipv4[0]
            phone = f"{int(ipaddress.IPv4Address(ip_address))}"
            print(f"  ✅ Success! Assigned IP: {ip_address}")
            print(f"       {phone}")
            if len(phone) == 10:
                print(f"       ✅ good length")

            # A tiny pause to be nice to Linode's API rate limits
            time.sleep(1)

    except Exception as e:
        print(f"\n⚠️ An error occurred during creation: {e}")

    finally:
        # 2. Clean up (The 'finally' block ensures this ALWAYS runs,
        # even if the code crashes halfway through the creation loop!)
        if created_linodes:
            print(
                f"\nCleaning up: Deleting {len(created_linodes)} Linodes to release IPs..."
            )

            for linode in created_linodes:
                try:
                    ip_address = linode.ipv4[0]
                    print(f"  🗑️ Deleting Linode {linode.id} ({ip_address})...")
                    linode.delete()
                except Exception as del_err:
                    print(
                        f"  ⚠️ Failed to delete Linode {linode.id}: {del_err}. Check console!"
                    )

            print("Clean up complete.")


if __name__ == "__main__":
    explore_ip_batch()
