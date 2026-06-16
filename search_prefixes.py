#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#     "telnyx",
#     "twilio",
# ]
# ///

import telnyx
import twilio.rest

import data
import secret

twilio_client = twilio.rest.Client(secret.TWILIO_SID, secret.TWILIO_CLIENT_SECRET)


def search_twilio(prefix):
    area_code = int(str(prefix)[:3])
    country_code = data.AREA_CODE_COUNTRY_CODES.get(area_code, "US")

    numbers = twilio_client.available_phone_numbers(country_code).local.list(
        contains=f"{prefix}****", sms_enabled=True
    )
    print("twilio", numbers)


def check_telnyx(ip):
    numbers = telnyx.AvailablePhoneNumber.list(
        filter={"phone_number": {"contains": target_number}}, limit=1
    )
    print("telnyx", numbers)

    if numbers:
        print(f"XXX FOUND {ip} XXX")
        linodes.pop()  # remove from deletion list
        twilio_client.incoming_phone_numbers.create(
            phone_number=numbers[0].phone_number
        )
        raise Exception("XXX FOUND XXX")


with open("prefixes.txt") as f:
    for line in f:
        prefix = line.strip()
        print(prefix)
        search_twilio(prefix)
