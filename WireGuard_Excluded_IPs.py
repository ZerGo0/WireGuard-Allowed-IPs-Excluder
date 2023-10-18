import ipaddress
import sys


def parse_ip_networks(ip_list_str):
    ip_list = ip_list_str.split(",")
    networks = []
    invalid_ip_addresses = []  # List to store invalid IPs.

    for ip in ip_list:
        ip = ip.strip()
        try:
            if "/" in ip:
                networks.append(ipaddress.ip_network(ip, strict=False))
            else:
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.version == 4:
                    networks.append(ipaddress.ip_network(f"{ip}/32", strict=False))
                else:
                    networks.append(ipaddress.ip_network(f"{ip}/128", strict=False))
        except ValueError:
            invalid_ip_addresses.append(ip)  # Add invalid IP to the list.

    return networks, invalid_ip_addresses  # Return both valid networks and invalid IPs.


def get_input_and_parse(prompt):
    while True:  # Keep looping until we break out.
        user_input = input(prompt)
        networks, invalid_ip_addresses = parse_ip_networks(
            user_input
        )  # Get both valid networks and invalid IPs.

        if not invalid_ip_addresses:  # If there are no invalid IPs, break the loop.
            break

        # If there are invalid IPs, notify the user and continue the loop.
        print("Invalid IPs or subnets: " + ", ".join(invalid_ip_addresses))
        print("Please try again. Ctrl+C to exit.")

    return networks


def exclude_networks(allowed_networks, disallowed_networks):
    remaining_networks = set(allowed_networks)

    for disallowed in disallowed_networks:
        new_remaining_networks = set()

        for allowed in remaining_networks:
            if allowed.version == disallowed.version:
                if disallowed.subnet_of(allowed):
                    # If the disallowed network is a subnet of the allowed network, exclude it
                    new_remaining_networks.update(allowed.address_exclude(disallowed))
                elif allowed.overlaps(disallowed):
                    # Handle partial overlap
                    new_remaining_networks.update(
                        handle_partial_overlap(allowed, disallowed)
                    )
                else:
                    # If there's no overlap, keep the allowed network as it is.
                    new_remaining_networks.add(allowed)
            else:
                # If the IP versions don't match, keep the allowed network as it is.
                new_remaining_networks.add(allowed)

        # Update the remaining networks after processing each disallowed network
        remaining_networks = new_remaining_networks

    return remaining_networks


def handle_partial_overlap(allowed, disallowed):
    # This function will handle the case of a partial overlap and return the non-overlapping portions of the allowed network.
    non_overlapping_networks = []

    # Calculate the IPs for the allowed and disallowed networks
    allowed_ips = list(allowed.hosts())
    disallowed_ips = set(disallowed.hosts())  # Use a set for faster lookup

    # Filter out the disallowed IPs
    allowed_ips = [ip for ip in allowed_ips if ip not in disallowed_ips]

    if not allowed_ips:
        # If no IPs are left, there's nothing to add
        return non_overlapping_networks

    # Create new network(s) from the remaining IPs.
    # This is a simplistic way and works on individual IPs, not ranges.
    # You might need a more efficient way to handle ranges of IPs, especially for large networks.
    for ip in allowed_ips:
        if ip.version == 4:
            non_overlapping_networks.append(
                ipaddress.ip_network(f"{ip}/32", strict=False)
            )
        else:
            non_overlapping_networks.append(
                ipaddress.ip_network(f"{ip}/128", strict=False)
            )

    return non_overlapping_networks


def sort_networks(networks):
    """Sort IP networks with all IPv4 first, then IPv6, each from lowest to highest."""
    ipv4 = []
    ipv6 = []
    for net in networks:
        if net.version == 4:
            ipv4.append(net)
        else:
            ipv6.append(net)
    # Sort each list individually
    ipv4_sorted = sorted(ipv4, key=lambda ip: ip.network_address)
    ipv6_sorted = sorted(ipv6, key=lambda ip: ip.network_address)

    # Combine the lists with all IPv4 addresses first, then IPv6
    return ipv4_sorted + ipv6_sorted


def main(unittest=False):
    allowed_input = ""
    disallowed_input = ""
    allowed_networks = []
    disallowed_networks = []

    # Validate command line arguments
    if len(sys.argv) == 3:
        allowed_input = sys.argv[1]
        disallowed_input = sys.argv[2]
    elif len(sys.argv) == 2:
        disallowed_input = sys.argv[1]
    else:
        print("Wrong number of arguments provided, falling back to interactive mode.")
        # Reset inputs to fall back to interactive mode
        allowed_input = ""
        disallowed_input = ""

    # Validate and parse command line arguments or get user input if arguments are invalid or not provided.
    if allowed_input:
        allowed_networks, invalid_allowed = parse_ip_networks(allowed_input)
        if invalid_allowed:
            print("Invalid Allowed IPs: " + ", ".join(invalid_allowed))
            allowed_networks = (
                []
            )  # Reset to empty to trigger interactive mode for allowed IPs

    if disallowed_input:  # This ensures it won't run if there's no disallowed_input
        disallowed_networks, invalid_disallowed = parse_ip_networks(disallowed_input)
        if invalid_disallowed:
            print("Invalid Disallowed IPs: " + ", ".join(invalid_disallowed))
            disallowed_networks = (
                []
            )  # Reset to empty to trigger interactive mode for disallowed IPs

    # If inputs were invalid or not provided, switch to interactive mode.
    if not allowed_networks and not len(sys.argv) == 2:
        allowed_networks = get_input_and_parse(
            "Enter the Allowed IPs, comma separated (e.g., 0.0.0.0/0):\n"
        )

    if not disallowed_networks:
        disallowed_networks = get_input_and_parse(
            "Enter the Disallowed IPs, comma separated (e.g., 10.0.0.0/8,127.0.0.0/8,172.16.0.0/12,192.168.0.0/16):\n"
        )

    # Process the IP networks.
    excluded_allowed_networks = exclude_networks(allowed_networks, disallowed_networks)

    # Sort the networks with IPv4 first, then IPv6.
    sorted_networks = sort_networks(excluded_allowed_networks)

    if not sorted_networks:
        print("Error: No IPs are allowed based on the provided input.")
        sys.exit(1)

    # Print the initial inputs and final result.
    print("Input:")
    print("AllowedIPs = " + ", ".join(map(str, allowed_networks)))
    print("DisallowedIPs = " + ", ".join(map(str, disallowed_networks)))
    print()
    print("=======================")
    print()
    print("Output:")
    print("AllowedIPs = " + ", ".join(map(str, sorted_networks)))

    if unittest:
        return sorted_networks


if __name__ == "__main__":
    main()
