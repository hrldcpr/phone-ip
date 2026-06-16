import httpx
import ipaddress


def get_linode_cidrs():
    # Linode's primary Autonomous System Number (ASN)
    asn = "63949"

    # Switching to RIPEstat's highly reliable official API
    url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={asn}"

    print(f"Fetching BGP prefixes for AS{asn} from RIPEstat...")

    headers = {"User-Agent": "Linode-IP-Math-Experiment/1.0"}

    try:
        with httpx.Client(headers=headers) as client:
            # RIPEstat can occasionally take a few seconds to aggregate data
            response = client.get(url, timeout=15.0)
            response.raise_for_status()
            data = response.json()

    except httpx.HTTPStatusError as exc:
        print(
            f"HTTP error response {exc.response.status_code} while requesting {exc.request.url!r}."
        )
        return
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}: {exc}")
        return

    # Extract all prefixes from the JSON response
    raw_prefixes = []

    # RIPEstat puts the prefixes inside data -> prefixes
    for prefix_obj in data.get("data", {}).get("prefixes", []):
        prefix = prefix_obj.get("prefix")

        # We only want IPv4 addresses (IPv6 contains colons and breaks the 10-digit math)
        if prefix and ":" not in prefix:
            raw_prefixes.append(prefix)

    print(f"Found {len(raw_prefixes)} raw IPv4 prefixes announced by Linode.")

    # Convert strings to IPv4Network objects
    network_objects = [ipaddress.IPv4Network(p) for p in raw_prefixes]

    # Clean up overlaps and route disaggregation
    collapsed_networks = list(ipaddress.collapse_addresses(network_objects))

    print(f"Collapsed down to {len(collapsed_networks)} deduplicated IP blocks.")

    # Write the clean list to a text file
    filename = "linode_cidrs.txt"
    with open(filename, "w") as f:
        for net in collapsed_networks:
            f.write(str(net) + "\n")

    print(f"Success! Deduplicated CIDRs saved to {filename}")


if __name__ == "__main__":
    get_linode_cidrs()
