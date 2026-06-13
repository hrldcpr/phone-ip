#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "twilio",
# ]
# ///

import ipaddress
import os
from twilio.rest import Client

import secret

client = Client(secret.TWILIO_SID, secret.TWILIO_CLIENT_SECRET)

# The prefix you want to check (e.g., the Area Code + Exchange)
TARGET_PREFIX = "289262"
COUNTRY = "CA"  # US or CA

print(f"Searching Twilio for numbers starting with {COUNTRY} {TARGET_PREFIX}...")

available_numbers = client.available_phone_numbers(COUNTRY).local.list(
    contains=f"{TARGET_PREFIX}****",  # The API DOES use the * wildcard!
    sms_enabled=True,
    limit=5,
)

if available_numbers:
    print(f"🎉 FOUND {len(available_numbers)} NUMBERS!")
    for num in available_numbers:
        print(f" - {num.phone_number}")
        try:
            print(f"   {ipaddress.ip_address(int(num.phone_number[-10:]))}")
        except:
            print(f"   bad IP tho")
else:
    print("❌ No numbers available in that block right now.")
