import ipaddress
import sys

def parse_ip_networks(ip_list):
    ipv4, ipv6 = [], []
    invalid_entries = []

    for ip in ip_list:
        ip = ip.strip()  # Ensure any extra spaces are removed
        try:
            if '/' in ip:
                # If there's a subnet mask, parse it as a network
                network = ipaddress.ip_network(ip, strict=False)
            else:
                # If there's no subnet mask, parse it as an IP and then get its respective network
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.version == 4:
                    network = ipaddress.ip_network(ip + '/32', strict=False)  # for IPv4
                else:
                    network = ipaddress.ip_network(ip + '/128', strict=False)  # for IPv6

            if network.version == 4:
                ipv4.append(network)
            else:
                ipv6.append(network)
        except ValueError:
            # If an error occurs, add the entry to a list of invalid entries
            invalid_entries.append(ip)

    if invalid_entries:
        # If there are any invalid entries, print them and return None to signal an error
        for entry in invalid_entries:
            print(f"Invalid IP or subnet: {entry}")
        return None

    return ipv4, ipv6



def calculate_remaining_ips(allowed_ips, disallowed_ips):
    remaining_ips = set(allowed_ips)
    for disallowed in disallowed_ips:
        remaining_ips -= set(disallowed.address_exclude(allowed) for allowed in allowed_ips if allowed.overlaps(disallowed))
    return remaining_ips

def main():
    if len(sys.argv) == 3:
        allowed_input = sys.argv[1]
        disallowed_input = sys.argv[2]
    else:
        print("\nYou can optionally provide command-line arguments as follows:")
        print("WireGuard_Excluded_IPs.py <AllowedIPs> <DisallowedIPs>")
        print("Example: WireGuard_Excluded_IPs.py '0.0.0.0/0' '10.0.0.0/8,127.0.0.0/8,172.16.0.0/12,192.168.0.0/16'")
        print("\nIf no arguments are provided, you will be prompted for input.\n")

        allowed_input = input("Enter the Allowed IPs, comma separated (e.g., 0.0.0.0/0):\n")
        disallowed_input = input("Enter the Disallowed IPs, comma separated (e.g., 10.0.0.0/8,127.0.0.0/8,172.16.0.0/12,192.168.0.0/16):\n")

    allowed_ips = parse_ip_networks(allowed_input.split(','))
    disallowed_ips = parse_ip_networks(disallowed_input.split(','))

    if allowed_ips is None or disallowed_ips is None:
        return

    # Separate IPv4 and IPv6 for both allowed and disallowed IPs
    allowed_ipv4, allowed_ipv6 = allowed_ips
    disallowed_ipv4, disallowed_ipv6 = disallowed_ips

    # Calculate remaining IPs for IPv4 and IPv6 separately
    remaining_ipv4 = calculate_remaining_ips(allowed_ipv4, disallowed_ipv4)
    remaining_ipv6 = calculate_remaining_ips(allowed_ipv6, disallowed_ipv6)

    # Sort IPv4 and IPv6 addresses separately
    sorted_remaining_ipv4 = sorted(remaining_ipv4)
    sorted_remaining_ipv6 = sorted(remaining_ipv6)

    # Concatenate the sorted lists and convert to strings
    all_remaining_ips = [str(ip) for ip in sorted_remaining_ipv4 + sorted_remaining_ipv6]
    print("AllowedIPs =", ', '.join(all_remaining_ips))

if __name__ == "__main__":
    main()
