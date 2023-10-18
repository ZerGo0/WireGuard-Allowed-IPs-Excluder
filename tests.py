from ipaddress import IPv4Network, IPv6Network
import sys
import unittest
from unittest import mock
from WireGuard_Excluded_IPs import main


class TestWireGuardExcludedIPs(unittest.TestCase):
    @mock.patch("WireGuard_Excluded_IPs.print")
    def test_basic_functionality_no_overlaps(self, _):
        sys.argv = [
            "WireGuard_Excluded_IPs.py",
            "192.168.1.0/24, 10.0.0.0/16",
            "192.168.2.0/24, 10.1.0.0/16",
        ]

        expected = [IPv4Network("10.0.0.0/16"), IPv4Network("192.168.1.0/24")]

        self.assertEqual(main(True), expected)

    @mock.patch("WireGuard_Excluded_IPs.print")
    def test_full_subnet_exclusion(self, _):
        sys.argv = ["WireGuard_Excluded_IPs.py", "192.168.1.0/24", "192.168.1.0/28"]

        expected = [
            IPv4Network("192.168.1.16/28"),
            IPv4Network("192.168.1.32/27"),
            IPv4Network("192.168.1.64/26"),
            IPv4Network("192.168.1.128/25"),
        ]

        self.assertEqual(main(True), expected)

    @mock.patch("WireGuard_Excluded_IPs.print")
    def test_ipv6_inclusion(self, _):
        sys.argv = ["WireGuard_Excluded_IPs.py", "2001:db8::/48", "2001:db8:1::/64"]

        expected = [IPv6Network("2001:db8::/48")]

        self.assertEqual(main(True), expected)

    @mock.patch("WireGuard_Excluded_IPs.print")
    def test_partial_overlap_new_logic(self, _):
        sys.argv = [
            "WireGuard_Excluded_IPs.py",
            "192.168.1.0/24",
            "192.168.1.0/28, 192.168.1.240/28",
        ]

        expected = [
            IPv4Network("192.168.1.16/28"),
            IPv4Network("192.168.1.32/27"),
            IPv4Network("192.168.1.64/26"),
            IPv4Network("192.168.1.128/26"),
            IPv4Network("192.168.1.192/27"),
            IPv4Network("192.168.1.224/28"),
        ]

        self.assertEqual(main(True), expected)

    @mock.patch("WireGuard_Excluded_IPs.print")
    def test_different_ip_versions(self, _):
        sys.argv = [
            "WireGuard_Excluded_IPs.py",
            "192.168.1.0/24, 2001:db8::/32",
            "2001:db8:aaaa::/48",
        ]

        expected = [
            IPv4Network("192.168.1.0/24"),
            IPv6Network("2001:db8::/33"),
            IPv6Network("2001:db8:8000::/35"),
            IPv6Network("2001:db8:a000::/37"),
            IPv6Network("2001:db8:a800::/39"),
            IPv6Network("2001:db8:aa00::/41"),
            IPv6Network("2001:db8:aa80::/43"),
            IPv6Network("2001:db8:aaa0::/45"),
            IPv6Network("2001:db8:aaa8::/47"),
            IPv6Network("2001:db8:aaab::/48"),
            IPv6Network("2001:db8:aaac::/46"),
            IPv6Network("2001:db8:aab0::/44"),
            IPv6Network("2001:db8:aac0::/42"),
            IPv6Network("2001:db8:ab00::/40"),
            IPv6Network("2001:db8:ac00::/38"),
            IPv6Network("2001:db8:b000::/36"),
            IPv6Network("2001:db8:c000::/34"),
        ]

        self.assertEqual(main(True), expected)

    @mock.patch("WireGuard_Excluded_IPs.input", return_value="192.168.1.0/32")
    @mock.patch("WireGuard_Excluded_IPs.print")
    def test_invalid_input(self, _, __):
        sys.argv = ["WireGuard_Excluded_IPs.py", "300.1.1.1, 192.168.1.0/33"]

        # We expect exit(1) because we patch the input to the same values for allowed an disallowed IPs
        with self.assertRaises(SystemExit) as cm:
            assert main(True)

        self.assertEqual(cm.exception.code, 1)

    @mock.patch("WireGuard_Excluded_IPs.print")
    def test_exclude_local_ips(self, _):
        sys.argv = [
            "WireGuard_Excluded_IPs.py",
            "0.0.0.0/0",
            "192.168.0.0/16, 10.0.0.0/8",
        ]

        expected = [
            IPv4Network("0.0.0.0/5"),
            IPv4Network("8.0.0.0/7"),
            IPv4Network("11.0.0.0/8"),
            IPv4Network("12.0.0.0/6"),
            IPv4Network("16.0.0.0/4"),
            IPv4Network("32.0.0.0/3"),
            IPv4Network("64.0.0.0/2"),
            IPv4Network("128.0.0.0/2"),
            IPv4Network("192.0.0.0/9"),
            IPv4Network("192.128.0.0/11"),
            IPv4Network("192.160.0.0/13"),
            IPv4Network("192.169.0.0/16"),
            IPv4Network("192.170.0.0/15"),
            IPv4Network("192.172.0.0/14"),
            IPv4Network("192.176.0.0/12"),
            IPv4Network("192.192.0.0/10"),
            IPv4Network("193.0.0.0/8"),
            IPv4Network("194.0.0.0/7"),
            IPv4Network("196.0.0.0/6"),
            IPv4Network("200.0.0.0/5"),
            IPv4Network("208.0.0.0/4"),
            IPv4Network("224.0.0.0/3"),
        ]

        self.assertEqual(main(True), expected)


if __name__ == "__main__":
    unittest.main()
