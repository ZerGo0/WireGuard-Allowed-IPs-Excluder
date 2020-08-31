import ipaddress
import re
import sys

arguments = sys.argv[1:]
if len(arguments) is 0:
    print("Syntax: WireGuard_Excluded_IPs.py 8.8.8.8 (1.1.1.1)")
    exit()

for arg in sys.argv[1:]:
    if re.search("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", arg) is None:
        print("Invalid IP Address: {}".format(arg))
        exit()
        break
    pass

mainBlockRange = ipaddress.ip_network('0.0.0.0/0')
listUpdatedMainBlockRange = list(mainBlockRange.address_exclude(
    ipaddress.ip_network('{}/32'.format(sys.argv[1]))))
listUpdatedMainBlockRange.reverse()
listMainBlockRange = listUpdatedMainBlockRange

for arg in sys.argv[1:]:
    tempIP = ipaddress.IPv4Address(arg)
    print("tempIP: {}".format(tempIP))
    i = 0

    for tempBlockRange in listUpdatedMainBlockRange:
        print("tempBlockRange: {}".format(tempBlockRange))
        if tempIP in tempBlockRange:
            print("tempIP: {} | tempBlockRange: {}".format(
                tempIP, tempBlockRange))
            listMainBlockRange.remove(tempBlockRange)
            tempRange = ipaddress.ip_network(tempBlockRange)
            listMainBlockRange.insert(i, list(
                tempRange.address_exclude(ipaddress.ip_network('{}/32'.format(arg)))))
        i += 1

    listUpdatedMainBlockRange = listMainBlockRange

listMainBlockRange.reverse()
print("\n\n\n")
print("AllowedIPs = {}, ::/1, 8000::/1".format(str(list(listMainBlockRange)).replace("[", "").replace(
    "IPv4Network('", "").replace("')", "").replace("]", "")))
