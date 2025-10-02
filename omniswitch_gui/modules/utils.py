import ipaddress

def ip(val: str) -> str:
    try:
        return str(ipaddress.ip_address(val))
    except Exception:
        return ""

def mask_ok(m: str) -> bool:
    try:
        ipaddress.IPv4Network(f"0.0.0.0/{m}")
        return True
    except Exception:
        return False

def same_subnet(ip1: str, mask1: str, ip2: str) -> bool:
    try:
        n1 = ipaddress.ip_network(f"{ip1}/{mask1}", strict=False)
        return ipaddress.ip_address(ip2) in n1
    except Exception:
        return False
