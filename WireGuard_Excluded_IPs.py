import ipaddress

def get_ip_networks_from_input(prompt):
    while True:
        ip_networks = []
        invalid_entries = []

        print(prompt)
        input_str = input()

        for ip in input_str.split(","):
            ip = ip.strip()
            if ip:  # avoid empty strings
                try:
                    # Attempt to create an ip_network object. Works for both IPv4 and IPv6.
                    network = ipaddress.ip_network(ip, strict=False)
                    ip_networks.append(network)
                except ValueError as e:
                    # If an error occurs, print the error and add to the list of invalid entries
                    print(f"Error: Invalid IP address/network: '{ip}'. Error details: {e}")
                    invalid_entries.append(ip)

        if not invalid_entries:
            return ip_networks  # return the list if all entries were valid
        else:
            print(f"Invalid entries: {', '.join(invalid_entries)}. Please re-enter the entire list of IPs.")

def main():
    print("This script calculates allowed IP ranges by excluding disallowed ranges from the allowed ones.\n")

    # Get the Allowed IPs from the user with an example
    allowed_ips = get_ip_networks_from_input("Enter the Allowed IPs, comma separated, ex: 0.0.0.0/0:")

    # Get the Disallowed IPs from the user with an example
    disallowed_ips = get_ip_networks_from_input("Enter the Disallowed IPs, comma separated, ex: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 127.0.0.0/8:")

    # Starting with the allowed networks, we'll subtract the disallowed ones
    remaining_networks = allowed_ips

    for disallowed in disallowed_ips:
        temp_remaining_networks = []
        for net in remaining_networks:
            if net.overlaps(disallowed):
                # If there's an overlap, we exclude the disallowed network and add the remaining ones
                temp_remaining_networks.extend(net.address_exclude(disallowed))
            else:
                # If there's no overlap, we keep the network as is
                temp_remaining_networks.append(net)
        remaining_networks = temp_remaining_networks

    # Print the final list of allowed IPs
    if remaining_networks:
        print("\nAllowedIPs =", ', '.join(str(net) for net in sorted(remaining_networks)))
    else:
        print("No remaining allowed IPs after exclusions.")

if __name__ == "__main__":
    main()
