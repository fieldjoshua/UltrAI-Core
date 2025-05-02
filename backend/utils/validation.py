"""
URL Validation Module.

This module provides utilities for validating URLs to prevent security vulnerabilities
such as Server-Side Request Forgery (SSRF) attacks.
"""

import os
import re
import socket
import ipaddress
from urllib.parse import urlparse
from typing import List, Optional, Set, Dict, Any

# Logger setup
import logging
logger = logging.getLogger(__name__)

# Get allowed domains from environment variables or use defaults
DEFAULT_ALLOWED_DOMAINS = [
    "api.openai.com",
    "api.anthropic.com",
    "generativelanguage.googleapis.com",
    "api.mistral.ai",
    "api.cohere.ai",
    "api.together.xyz",
]

# Private/internal IP ranges to block
PRIVATE_IP_RANGES = [
    '0.0.0.0/8',          # Current network
    '10.0.0.0/8',         # Private network
    '100.64.0.0/10',      # Shared address space
    '127.0.0.0/8',        # Localhost
    '169.254.0.0/16',     # Link-local
    '172.16.0.0/12',      # Private network
    '192.0.0.0/24',       # IETF protocol assignments
    '192.0.2.0/24',       # TEST-NET-1
    '192.168.0.0/16',     # Private network
    '198.18.0.0/15',      # Benchmark testing
    '198.51.100.0/24',    # TEST-NET-2
    '203.0.113.0/24',     # TEST-NET-3
    '224.0.0.0/4',        # Multicast
    '240.0.0.0/4',        # Reserved for future use
    '255.255.255.255/32', # Broadcast
    'fc00::/7',           # Unique local address
    'fe80::/10',          # Link-local address
    '::1/128',            # Localhost
]


class URLValidator:
    """
    URL Validator class for preventing SSRF and other URL-based attacks.
    """

    def __init__(self):
        """Initialize the URL validator."""
        # Parse allowed domains from environment
        self.allowed_domains = self._parse_allowed_domains()
        # Parse private IP ranges
        self.private_ip_ranges = [ipaddress.ip_network(cidr) for cidr in PRIVATE_IP_RANGES]
        # Initialize cached IP resolutions to avoid repeated DNS lookups
        self.cached_ip_resolutions: Dict[str, List[str]] = {}

    def _parse_allowed_domains(self) -> Set[str]:
        """
        Parse allowed domains from environment variables.
        
        Returns:
            Set of allowed domains
        """
        # Get allowed domains from environment
        env_domains = os.environ.get('ALLOWED_EXTERNAL_DOMAINS', '')
        
        # If environment variable is not set, use defaults
        if not env_domains:
            logger.info(f"Using default allowed domains: {DEFAULT_ALLOWED_DOMAINS}")
            return set(DEFAULT_ALLOWED_DOMAINS)
        
        # Split by comma and strip whitespace
        domains = [domain.strip() for domain in env_domains.split(',')]
        valid_domains = [d for d in domains if d]  # Remove empty entries
        
        if not valid_domains:
            logger.warning("No valid domains specified in ALLOWED_EXTERNAL_DOMAINS, using defaults")
            return set(DEFAULT_ALLOWED_DOMAINS)
        
        logger.info(f"Using allowed domains from environment: {valid_domains}")
        return set(valid_domains)

    def _is_domain_allowed(self, domain: str) -> bool:
        """
        Check if a domain is in the allowed list.
        
        Args:
            domain: Domain name to check
            
        Returns:
            True if domain is allowed, False otherwise
        """
        # Check for exact match
        if domain in self.allowed_domains:
            return True
        
        # Check for subdomain match
        for allowed_domain in self.allowed_domains:
            if domain.endswith(f".{allowed_domain}"):
                return True
                
        return False

    def _is_ip_private(self, ip_str: str) -> bool:
        """
        Check if an IP address is in a private/reserved range.
        
        Args:
            ip_str: IP address as string
            
        Returns:
            True if IP is private, False otherwise
        """
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            
            # Check against private IP ranges
            for ip_range in self.private_ip_ranges:
                if ip_obj in ip_range:
                    return True
                    
            return False
        except ValueError:
            # If we can't parse the IP, consider it invalid
            logger.warning(f"Could not parse IP address: {ip_str}")
            return True

    def _resolve_domain(self, domain: str) -> List[str]:
        """
        Resolve domain to IP addresses.
        
        Args:
            domain: Domain name to resolve
            
        Returns:
            List of resolved IP addresses
        """
        # Check cache first
        if domain in self.cached_ip_resolutions:
            return self.cached_ip_resolutions[domain]
            
        try:
            # Get IP addresses for the domain (both IPv4 and IPv6)
            ip_list = []
            for addrinfo in socket.getaddrinfo(domain, None):
                ip = addrinfo[4][0]
                if ip not in ip_list:
                    ip_list.append(ip)
                    
            # Cache the results
            self.cached_ip_resolutions[domain] = ip_list
            return ip_list
        except socket.gaierror:
            logger.warning(f"Could not resolve domain: {domain}")
            return []

    def is_url_safe(self, url: str, check_ips: bool = True) -> bool:
        """
        Check if a URL is safe from SSRF attacks.
        
        Args:
            url: URL to validate
            check_ips: Whether to also check resolved IP addresses
            
        Returns:
            True if URL is safe, False otherwise
        """
        try:
            # Parse the URL
            parsed_url = urlparse(url)
            
            # Check scheme (only allow http and https)
            if parsed_url.scheme not in ['http', 'https']:
                logger.warning(f"URL scheme not allowed: {parsed_url.scheme}")
                return False
                
            # Get domain without port
            domain = parsed_url.netloc.split(':')[0] if ':' in parsed_url.netloc else parsed_url.netloc
            
            # Check for IP address in hostname
            is_ip = re.match(r'^(?:\d{1,3}\.){3}\d{1,3}$', domain) is not None
            
            if is_ip:
                # Direct IP access is not allowed
                logger.warning(f"Direct IP address in URL not allowed: {domain}")
                return False
                
            # Check if domain is allowed
            if not self._is_domain_allowed(domain):
                logger.warning(f"Domain not in allowed list: {domain}")
                return False
                
            # Check resolved IPs if requested
            if check_ips:
                ip_addresses = self._resolve_domain(domain)
                
                for ip in ip_addresses:
                    if self._is_ip_private(ip):
                        logger.warning(f"Domain {domain} resolves to private IP: {ip}")
                        return False
                        
            return True
        except Exception as e:
            logger.error(f"Error validating URL: {e}")
            return False

    def validate_url(self, url: str, check_ips: bool = True) -> None:
        """
        Validate URL and raise ValueError if not safe.
        
        Args:
            url: URL to validate
            check_ips: Whether to also check resolved IP addresses
            
        Raises:
            ValueError: If URL is not safe
        """
        if not self.is_url_safe(url, check_ips):
            raise ValueError(f"URL validation failed: {url} is not allowed")


# Create singleton instance
url_validator = URLValidator()


def validate_url(url: str, check_ips: bool = True) -> None:
    """
    Validate URL and raise ValueError if not safe.
    
    Args:
        url: URL to validate
        check_ips: Whether to also check resolved IP addresses
        
    Raises:
        ValueError: If URL is not safe
    """
    url_validator.validate_url(url, check_ips)


def is_url_safe(url: str, check_ips: bool = True) -> bool:
    """
    Check if a URL is safe from SSRF attacks.
    
    Args:
        url: URL to validate
        check_ips: Whether to also check resolved IP addresses
        
    Returns:
        True if URL is safe, False otherwise
    """
    return url_validator.is_url_safe(url, check_ips)