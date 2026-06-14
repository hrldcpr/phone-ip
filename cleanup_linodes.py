#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#     "linode_api4",
# ]
# ///

import os
from linode_api4 import LinodeClient

import secret


def cleanup_orphans():
    print("Initializing Linode client to hunt for orphans...")
    client = LinodeClient(secret.LINODE_PERSONAL_ACCESS_TOKEN)

    try:
        # Fetch every instance on your account (the SDK handles pagination for you!)
        all_instances = client.linode.instances()

        deleted_count = 0
        for instance in all_instances:

            if instance.label.startswith("linode"):
                ip_address = instance.ipv4[0] if instance.ipv4 else "No IP"
                print(
                    f"  🗑️ Found orphan! Deleting {instance.label} (IP: {ip_address})..."
                )

                instance.delete()
                deleted_count += 1

            else:
                print(f"  ⏭️ Skipping {instance.label} (Safe!)")

        print(f"\n✅ Cleanup complete. Vaporized {deleted_count} orphaned Linodes.")

    except Exception as e:
        print(f"\n⚠️ An error occurred during cleanup: {e}")


if __name__ == "__main__":
    cleanup_orphans()
