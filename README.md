# WireGuard-Allowed-IPs-Excluder
Use the following form when you need to calculate complex AllowedIPs settings for a WireGuard peer, by subtracting the “disallowed” IP address blocks from the “allowed” IP address blocks.

```
Syntax: WireGuard-Allowed-IPs-Excluders.py [AllowedIPs] [DisallowedIPs]
Example: python WireGuard-Allowed-IPs-Excluders.py "0.0.0.0/0" "192.168.0.0/16, 10.0.0.0/8"
```

For example, say you wanted to route everything in the `10.0.0.0/8` block of IP addresses through a WireGuard peer — except you also wanted to exclude the smaller `10.0.1.0/24` block from it. In the `Allowed IPs` field, input `10.0.0.0/8`; in the `Disallowed IPs` field, input `10.0.1.0/24`; and click the Calculate button. This is the result you’ll get (which is what you enter into your WireGuard config):

```
AllowedIPs = 10.0.0.0/24, 10.0.2.0/23, 10.0.4.0/22, 10.0.8.0/21, 10.0.16.0/20, 10.0.32.0/19, 10.0.64.0/18, 10.0.128.0/17, 10.1.0.0/16, 10.2.0.0/15, 10.4.0.0/14, 10.8.0.0/13, 10.16.0.0/12, 10.32.0.0/11, 10.64.0.0/10, 10.128.0.0/9
```

Or as another example, say you wanted to route everything but the standard private, local, or link-scoped IP address blocks through a WireGuard peer. In the `Allowed IPs` field, input `0.0.0.0/0`, `::/0`; in the `Disallowed IPs` field, input `0.0.0.0/8`, `10.0.0.0/8`, `127.0.0.0/8`, `169.254.0.0/16`, `172.16.0.0/12`, `192.168.0.0/16`, `240.0.0.0/4`, `fc00::/7`, `fe80::/10`; and click the Calculate button. This is the result you’ll get:

```
AllowedIPs = 1.0.0.0/8, 2.0.0.0/7, 4.0.0.0/6, 8.0.0.0/7, 11.0.0.0/8, 12.0.0.0/6, 16.0.0.0/4, 32.0.0.0/3, 64.0.0.0/3, 96.0.0.0/4, 112.0.0.0/5, 120.0.0.0/6, 124.0.0.0/7, 126.0.0.0/8, 128.0.0.0/3, 160.0.0.0/5, 168.0.0.0/8, 169.0.0.0/9, 169.128.0.0/10, 169.192.0.0/11, 169.224.0.0/12, 169.240.0.0/13, 169.248.0.0/14, 169.252.0.0/15, 169.255.0.0/16, 170.0.0.0/7, 172.0.0.0/12, 172.32.0.0/11, 172.64.0.0/10, 172.128.0.0/9, 173.0.0.0/8, 174.0.0.0/7, 176.0.0.0/4, 192.0.0.0/9, 192.128.0.0/11, 192.160.0.0/13, 192.169.0.0/16, 192.170.0.0/15, 192.172.0.0/14, 192.176.0.0/12, 192.192.0.0/10, 193.0.0.0/8, 194.0.0.0/7, 196.0.0.0/6, 200.0.0.0/5, 208.0.0.0/4, 224.0.0.0/4, `::/1`, `8000::/2`, `c000::/3`, `e000::/4`, `f000::/5`, `f800::/6`, `fe00::/9`, `fec0::/10`, `ff00::/8`
```

BACKGROUND

You use the `AllowedIPs` setting of WireGuard to configure which blocks of IP addresses should be routed through which remote WireGuard peers. If you want to access everything through a peer, configure its `AllowedIPs` setting to the following:

```
AllowedIPs = 0.0.0.0/0, ::/0
```

This indicates to WireGuard that all IPv4 addresses (`0.0.0.0/0`) and all IPv6 addresses (`::/0`) should be routed through the peer. Note that you can specify multiple blocks of addresses on the same line, separated by commas, like above; or you can specify them individually on separate lines, like below:

```
AllowedIPs = 0.0.0.0/0
AllowedIPs = ::/0
```

If you want to access just a single block of IP addresses through a WireGuard peer, like say a block of IP addresses at a remote site that range from `192.168.100.0` to `192.168.100.255`, you’d set the `AllowedIPs` for it to the following:

```
AllowedIPs = 192.168.100.0/24
```

This indicates to WireGuard that only the `192.168.100.0/24` block of IP addresses should be routed through the peer. If you want to access multiple blocks of IP addresses through a WireGuard peer, you’d set the `AllowedIPs` for it to the following:

```
AllowedIPs = 192.168.100.0/24, 192.168.101.0/24
```

This indicates to WireGuard that both the `192.168.100.0/24` and `192.168.101.0/24` blocks of IP addresses should be routed through the peer. If you want to access everything but a certain block of IP addresses through a WireGuard peer, you’d set the `AllowedIPs` for it to the following:

```
AllowedIPs = 0.0.0.0/0, ::/0
```

And then you’d add a route on your local system to access that block of IP addresses through your regular Internet connection, like so:

```
`ip route add 192.168.100.0/24 via 192.168.1.1 dev eth0`
`ip route del 192.168.100.0/24 via 192.168.1.1 dev eth0`
```

You’d replace `192.168.1.1` with the IP address of your regular Internet gateway, and `eth0` with the name of your regular Internet network interface.

But what if you want to access everything but certain blocks of IP addresses through a WireGuard peer? This is where it gets complicated, because you can’t just add a route on your local system for each block of IP addresses you don’t want to access through the peer, because your system will still send packets to those IP addresses to the peer if its `AllowedIPs` is set to the following:

```
AllowedIPs = 0.0.0.0/0, ::/0
```

Instead, you need to set the `AllowedIPs` for the peer to everything but those blocks of IP addresses. And this is where our `AllowedIPs` Calculator comes in: It lets you easily calculate the `AllowedIPs` setting for a WireGuard peer by subtracting the “disallowed” IP address blocks from the “allowed” IP address blocks.

For example, say you wanted to access everything but the `10.0.0.0/8` block of IP addresses through a WireGuard peer. You’d input the following into the Calculator:

`Allowed IPs`: `0.0.0.0/0`, `::/0`
`Disallowed IPs`: `10.0.0.0/8`

And this is the result you’d get:

```
AllowedIPs = 0.0.0.0/5, 8.0.0.0/7, 11.0.0.0/8, 12.0.0.0/6, 16.0.0.0/4, 32.0.0.0/3, 64.0.0.0/2, 128.0.0.0/1, ::/0
```

Or as another example, say you wanted to access everything but the standard private, local, or link-scoped IP address blocks through a WireGuard peer. You’d input the following into the Calculator:

`Allowed IPs`: `0.0.0.0/0`, `::/0`
`Disallowed IPs`: `0.0.0.0/8`, `10.0.0.0/8`, `127.0.0.0/8`, `169.254.0.0/16`, `172.16.0.0/12`, `192.168.0.0/16`, `240.0.0.0/4`, `fc00::/7`, `fe80::/10`

And this is the result you’d get:

```
AllowedIPs = 1.0.0.0/8, 2.0.0.0/7, 4.0.0.0/6, 8.0.0.0/7, 11.0.0.0/8, 12.0.0.0/6, 16.0.0.0/4, 32.0.0.0/3, 64.0.0.0/3, 96.0.0.0/4, 112.0.0.0/5, 120.0.0.0/6, 124.0.0.0/7, 126.0.0.0/8, 128.0.0.0/3, 160.0.0.0/5, 168.0.0.0/8, 169.0.0.0/9, 169.128.0.0/10, 169.192.0.0/11, 169.224.0.0/12, 169.240.0.0/13, 169.248.0.0/14, 169.252.0.0/15, 169.255.0.0/16, 170.0.0.0/7, 172.0.0.0/12, 172.32.0.0/11, 172.64.0.0/10, 172.128.0.0/9, 173.0.0.0/8, 174.0.0.0/7, 176.0.0.0/4, 192.0.0.0/9, 192.128.0.0/11, 192.160.0.0/13, 192.169.0.0/16, 192.170.0.0/15, 192.172.0.0/14, 192.176.0.0/12, 192.192.0.0/10, 193.0.0.0/8, 194.0.0.0/7, 196.0.0.0/6, 200.0.0.0/5, 208.0.0.0/4, 224.0.0.0/4, `::/1`, `8000::/2`, `c000::/3`, `e000::/4`, `f000::/5`, `f800::/6`, `fe00::/9`, `fec0::/10`, `ff00::/8`
```

This indicates to WireGuard that everything but the specified blocks of IP addresses should be routed through the peer.

The Calculator works by first expanding the “allowed” and “disallowed” IP address blocks into their individual IP addresses, and then subtracting the “disallowed” IP addresses from the “allowed” IP addresses. It then combines the resulting IP addresses back into blocks, and sorts and merges those blocks to produce the final `AllowedIPs` setting.

The Calculator supports both IPv4 and IPv6 addresses, and you can input the IP address blocks into it in CIDR notation (like `192.168.100.0/24` or `::/0`) or with a subnet mask (like `192.168.100.0/255.255.255.0` or `::/128`). It also supports the special IP address blocks `0.0.0.0/0` and `::/0`, which represent all IPv4 addresses and all IPv6 addresses, respectively.
