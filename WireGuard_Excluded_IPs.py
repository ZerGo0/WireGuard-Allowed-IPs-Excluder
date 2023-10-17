import ipaddress
import sys

def parse_ip_networks(ip_list_str):
    ip_list = ip_list_str.split(',')
    networks = []
    invalid_ips = []  # List to store invalid IPs.

    for ip in ip_list:
        ip = ip.strip()
        try:
            if '/' in ip:
                networks.append(ipaddress.ip_network(ip, strict=False))
            else:
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.version == 4:
                    networks.append(ipaddress.ip_network(f"{ip}/32", strict=False))
                else:
                    networks.append(ipaddress.ip_network(f"{ip}/128", strict=False))
        except ValueError:
            invalid_ips.append(ip)  # Add invalid IP to the list.

    return networks, invalid_ips  # Return both valid networks and invalid IPs.

def get_input_and_parse(prompt):
    while True:  # Keep looping until we break out.
        user_input = input(prompt)
        networks, invalid_ips = parse_ip_networks(user_input)  # Get both valid networks and invalid IPs.

        if not invalid_ips:  # If there are no invalid IPs, break the loop.
            break

        # If there are invalid IPs, notify the user and continue the loop.
        print("Invalid IPs or subnets: " + ", ".join(invalid_ips))

    return networks


def exclude_networks(allowed_networks, disallowed_networks):
    remaining_networks = set(allowed_networks)
    for disallowed in disallowed_networks:
        for allowed in allowed_networks:
            if allowed.overlaps(disallowed):
                remaining_networks.difference_update([allowed])
                remaining_networks.update(allowed.address_exclude(disallowed))
    return remaining_networks

def sort_networks(networks):
    ipv4 = []
    ipv6 = []
    for net in networks:
        if net.version == 4:
            ipv4.append(net)
        else:
            ipv6.append(net)
    return sorted(ipv4) + sorted(ipv6)

def main():
    if len(sys.argv) == 3:
        allowed_input = sys.argv[1]
        disallowed_input = sys.argv[2]
        allowed_networks = parse_ip_networks(allowed_input.split(','))
        disallowed_networks = parse_ip_networks(disallowed_input.split(','))
    else:
        print("You can optionally provide command-line arguments as follows:")
        print("WireGuard_Excluded_IPs.py <AllowedIPs> <DisallowedIPs>")
        print("Example: WireGuard_Excluded_IPs.py '0.0.0.0/0' '10.0.0.0/8,127.0.0.0/8,172.16.0.0/12,192.168.0.0/16'\n")
        print("If no arguments are provided, you will be prompted for input.\n")

        allowed_networks = get_input_and_parse("Enter the Allowed IPs, comma separated (e.g., 0.0.0.0/0):\n")
        disallowed_networks = get_input_and_parse("Enter the Disallowed IPs, comma separated (e.g., 10.0.0.0/8,127.0.0.0/8,172.16.0.0/12,192.168.0.0/16):\n")

    if allowed_networks is None or disallowed_networks is None:
        return

    remaining_networks = exclude_networks(allowed_networks, disallowed_networks)
    sorted_networks = sort_networks(remaining_networks)

    print("AllowedIPs =", ', '.join(str(net) for net in sorted_networks))

if __name__ == "__main__":
    main()
