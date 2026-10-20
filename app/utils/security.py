import urllib.parse
import socket
import ipaddress
from typing import Tuple

# The explicit list of platforms we attempt to support
ALLOWED_DOMAINS = [
    "chatgpt.com",
    "chat.openai.com",
    "g.co",
    "gemini.google.com"
]

def is_valid_url(url: str) -> Tuple[bool, str]:
    """
    Validates the URL scheme, domain, and prevents SSRF.
    Returns a tuple: (is_valid, error_message)
    """
    try:
        parsed = urllib.parse.urlparse(url)
        
        # 1. Enforce safe schemes
        if parsed.scheme not in ["http", "https"]:
            return False, "Unsupported URL scheme. Only http and https are allowed."
            
        # 2. Extract and validate hostname
        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid URL format."
            
        # Allow exact domain matches or valid subdomains
        is_allowed_domain = any(
            hostname == domain or hostname.endswith(f".{domain}") 
            for domain in ALLOWED_DOMAINS
        )
        
        if not is_allowed_domain:
            return False, f"Unsupported platform. Supported domains: {', '.join(ALLOWED_DOMAINS)}"
            
        # 3. SSRF Prevention: Resolve IP and block internal networks
        try:
            ip_addr = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip_addr)
            
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast:
                return False, "Security error: URL resolves to an internal network address."
        except socket.gaierror:
            return False, "Could not resolve the domain name."
            
        return True, ""
        
    except Exception as e:
        return False, f"URL validation failed: {str(e)}"