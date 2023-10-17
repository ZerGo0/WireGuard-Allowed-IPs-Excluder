import ipaddress
import sys

def get_ip_networks(input_str):
    ip_networks = []
    invalid_entries = []

    for ip in input_str.split(","):
        ip = ip.strip()
        if ip:  # avoid empty strings
            try:
                # Attempt to create an ip_network object. Works for both IPv4 and IPv6.
                network = ipaddress.ip_network(ip, strict=False)
                ip_networks.append(network)
            except ValueError:
                # If an error occurs, add to the list of invalid entries
                invalid_entries.append(ip)

    return ip_networks, invalid_entries

def get_input(prompt):
    while True:
        input_str = input(prompt)
        ip_networks, invalid_entries = get_ip_networks(input_str)

        if invalid_entries:
            print(f"Invalid entries detected: {', '.join(invalid_entries)}. Please try again.")
        else:
            return ip_networks

def main():
    allowed_ips = []
    disallowed_ips = []

    # Check if the arguments are passed
    if len(sys.argv) == 3:
        allowed_ips, invalid_entries = get_ip_networks(sys.argv[1])
        if invalid_entries:
            print(f"Invalid Allowed IPs detected: {', '.join(invalid_entries)}")
            return

        disallowed_ips, invalid_entries = get_ip_networks(sys.argv[2])
        if invalid_entries:
            print(f"Invalid Disallowed IPs detected: {', '.join(invalid_entries)}")
            return
    else:
        print("You can optionally provide command-line arguments as follows:")
        print("WireGuard-Allowed-IPs-Excluders.py <AllowedIPs> <DisallowedIPs>")
        print("Example: WireGuard-Allowed-IPs-Excluders.py '0.0.0.0/0' '10.0.0.0/8,127.0.0.0/8,172.16.0.0/12,192.168.0.0/16'")
        print("\nIf no arguments are provided, you will be prompted for input.\n")

        # No arguments passed, ask for user input
        allowed_ips = get_input("Enter the Allowed IPs, comma separated (e.g., 0.0.0.0/0):\n")
        disallowed_ips = get_input("Enter the Disallowed IPs, comma separated (e.g., 10.0.0.0/8,127.0.0.0/8,172.16.0.0/12,192.168.0.0/16):\n")

    # Process the IP networks
    remaining_networks = allowed_ips

    for disallowed in disallowed_ips:
        temp_remaining_networks = []

        for net in remaining_networks:
            if net.overlaps(disallowed):
                temp_remaining_networks.extend(net.address_exclude(disallowed))
            else:
                temp_remaining_networks.append(net)

        remaining_networks = temp_remaining_networks

    # Print the final list of allowed IPs
    if remaining_networks:
        print("AllowedIPs =", ', '.join(str(net) for net in sorted(remaining_networks)))
    else:
        print("No remaining allowed IPs after exclusions.")

if __name__ == "__main__":
    main()
