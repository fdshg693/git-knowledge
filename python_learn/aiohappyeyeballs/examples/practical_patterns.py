"""
Practical Usage Patterns for aiohappyeyeballs

This module shows real-world usage patterns and best practices
for the aiohappyeyeballs library.
"""

import asyncio
import socket
import time
from typing import List, Tuple, Optional

# Note: These imports would work if aiohappyeyeballs is installed
# For demonstration purposes, we're showing the correct API patterns
# from aiohappyeyeballs import start_connection, addr_to_addr_infos, remove_addr_infos


async def dns_cache_with_happy_eyeballs():
    """
    Demonstrate using aiohappyeyeballs with a DNS cache.
    This is the primary use case for the library.
    """
    print("=== DNS Cache with Happy Eyeballs Example ===")

    class DNSCache:
        def __init__(self):
            self.cache = {}

        async def resolve(self, hostname: str, port: int) -> List[Tuple]:
            """Resolve hostname and cache the result."""
            cache_key = f"{hostname}:{port}"

            if cache_key not in self.cache:
                print(f"Resolving {hostname}:{port}...")
                loop = asyncio.get_event_loop()
                addr_infos = await loop.getaddrinfo(
                    hostname, port, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM
                )
                self.cache[cache_key] = addr_infos
                print(f"Cached {len(addr_infos)} addresses for {hostname}")
            else:
                print(f"Using cached addresses for {hostname}")

            return self.cache[cache_key]

    # Initialize DNS cache
    dns_cache = DNSCache()

    # Function to connect using cached DNS with Happy Eyeballs
    async def connect_with_cache(hostname: str, port: int):
        # Get cached or resolved addresses
        addr_infos = await dns_cache.resolve(hostname, port)

        # Connect using Happy Eyeballs
        # sock = await start_connection(addr_infos)
        print(f"Would connect to {hostname}:{port} using Happy Eyeballs")
        print(f"Available addresses: {len(addr_infos)}")

        # Simulate connection success
        await asyncio.sleep(0.1)
        return f"Connected to {hostname}:{port}"

    # Test multiple connections to the same host
    hosts = ["httpbin.org", "httpbin.org", "example.com", "httpbin.org"]
    ports = [80, 443, 80, 80]

    tasks = [connect_with_cache(host, port) for host, port in zip(hosts, ports)]
    results = await asyncio.gather(*tasks)

    for result in results:
        print(f"Result: {result}")


async def microservice_communication():
    """
    Demonstrate Happy Eyeballs for microservice-to-microservice communication.
    """
    print("\\n=== Microservice Communication Example ===")

    class ServiceDiscovery:
        """Simulated service discovery with multiple endpoints."""

        def __init__(self):
            self.services = {
                "user-service": [
                    ("user-service-1.internal", 8080),
                    ("user-service-2.internal", 8080),
                    ("192.168.1.10", 8080),  # IPv4 fallback
                ],
                "payment-service": [
                    ("payment-service.internal", 9090),
                    ("::1", 9090),  # IPv6 localhost
                    ("127.0.0.1", 9090),  # IPv4 localhost
                ],
            }

        async def get_endpoints(self, service_name: str) -> List[Tuple]:
            """Get all available endpoints for a service."""
            endpoints = self.services.get(service_name, [])

            # Convert to addr_info format
            addr_infos = []
            for host, port in endpoints:
                try:
                    # In real code, you'd use the actual DNS resolution
                    print(f"Would resolve {host}:{port}")
                    # Simulate addr_info structure
                    if ":" in host and "." not in host:  # IPv6
                        addr_info = (
                            socket.AF_INET6,
                            socket.SOCK_STREAM,
                            6,
                            "",
                            (host, port, 0, 0),
                        )
                    else:  # IPv4 or hostname
                        addr_info = (
                            socket.AF_INET,
                            socket.SOCK_STREAM,
                            6,
                            "",
                            (host, port),
                        )
                    addr_infos.append(addr_info)
                except Exception as e:
                    print(f"Failed to resolve {host}: {e}")

            return addr_infos

    # Service discovery instance
    discovery = ServiceDiscovery()

    async def call_service(service_name: str, request_data: str):
        """Make a call to a microservice using Happy Eyeballs."""
        try:
            # Get service endpoints
            addr_infos = await discovery.get_endpoints(service_name)

            if not addr_infos:
                raise Exception(f"No endpoints found for {service_name}")

            print(f"Calling {service_name} with {len(addr_infos)} endpoints")

            # Connect using Happy Eyeballs
            # sock = await start_connection(addr_infos, happy_eyeballs_delay=0.1)
            print(f"Would connect to {service_name} using Happy Eyeballs")

            # Simulate successful call
            await asyncio.sleep(0.05)
            return f"Response from {service_name}: processed '{request_data}'"

        except Exception as e:
            print(f"Failed to call {service_name}: {e}")
            return None

    # Test microservice calls
    services_to_call = [
        ("user-service", "get_user_123"),
        ("payment-service", "process_payment"),
        ("user-service", "update_user_456"),
    ]

    for service, request in services_to_call:
        result = await call_service(service, request)
        print(f"Call result: {result}")


async def load_balancer_with_health_checks():
    """
    Demonstrate a load balancer that uses Happy Eyeballs with health checking.
    """
    print("\\n=== Load Balancer with Health Checks Example ===")

    class HealthAwareLoadBalancer:
        def __init__(self):
            self.backends = [
                ("backend-1.example.com", 8080),
                ("backend-2.example.com", 8080),
                ("192.168.1.100", 8080),  # IPv4 backup
                ("2001:db8::100", 8080),  # IPv6 backup
            ]
            self.healthy_backends = set(self.backends)
            self.last_health_check = 0

        async def health_check(self):
            """Perform health checks on all backends."""
            current_time = time.time()
            if current_time - self.last_health_check < 30:  # Check every 30 seconds
                return

            print("Performing health checks...")
            self.last_health_check = current_time

            healthy = set()
            for host, port in self.backends:
                try:
                    # Simulate health check
                    print(f"Health checking {host}:{port}")

                    # In real code:
                    # addr_infos = await loop.getaddrinfo(host, port, ...)
                    # sock = await asyncio.wait_for(start_connection(addr_infos), timeout=5.0)
                    # # Send health check request
                    # sock.close()

                    # Simulate some backends being healthy
                    if "backend-1" in host or "192.168.1.100" in host:
                        healthy.add((host, port))
                        print(f"✓ {host}:{port} is healthy")
                    else:
                        print(f"✗ {host}:{port} is unhealthy")

                except Exception as e:
                    print(f"✗ Health check failed for {host}:{port}: {e}")

            self.healthy_backends = healthy
            print(f"Healthy backends: {len(self.healthy_backends)}")

        async def get_backend_addresses(self) -> List[Tuple]:
            """Get addresses for healthy backends only."""
            await self.health_check()

            addr_infos = []
            loop = asyncio.get_event_loop()

            for host, port in self.healthy_backends:
                try:
                    # In real implementation:
                    # backend_addrs = await loop.getaddrinfo(host, port, ...)
                    # addr_infos.extend(backend_addrs)

                    # Simulate addr_info
                    if "2001:db8" in host:  # IPv6
                        addr_info = (
                            socket.AF_INET6,
                            socket.SOCK_STREAM,
                            6,
                            "",
                            (host, port, 0, 0),
                        )
                    else:  # IPv4
                        addr_info = (
                            socket.AF_INET,
                            socket.SOCK_STREAM,
                            6,
                            "",
                            (host, port),
                        )
                    addr_infos.append(addr_info)

                except Exception as e:
                    print(f"Failed to resolve healthy backend {host}: {e}")

            return addr_infos

        async def forward_request(self, request_data: str):
            """Forward a request to a healthy backend."""
            addr_infos = await self.get_backend_addresses()

            if not addr_infos:
                raise Exception("No healthy backends available")

            # Use Happy Eyeballs to connect to the first available healthy backend
            # sock = await start_connection(addr_infos, happy_eyeballs_delay=0.1)
            print(f"Would forward request using {len(addr_infos)} healthy backends")

            # Simulate request processing
            await asyncio.sleep(0.02)
            return f"Request '{request_data}' processed by backend"

    # Test the load balancer
    lb = HealthAwareLoadBalancer()

    # Process multiple requests
    requests = ["request_1", "request_2", "request_3"]

    for request in requests:
        try:
            result = await lb.forward_request(request)
            print(f"Load balancer result: {result}")
        except Exception as e:
            print(f"Load balancer failed: {e}")


async def connection_retry_with_backoff():
    """
    Demonstrate retry logic with exponential backoff using Happy Eyeballs.
    """
    print("\\n=== Connection Retry with Backoff Example ===")

    class RetryableConnection:
        def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
            self.max_retries = max_retries
            self.base_delay = base_delay

        async def connect_with_retry(self, hostname: str, port: int):
            """Connect with exponential backoff retry."""

            for attempt in range(self.max_retries + 1):
                try:
                    print(
                        f"Connection attempt {attempt + 1}/{self.max_retries + 1} to {hostname}:{port}"
                    )

                    # Resolve addresses
                    loop = asyncio.get_event_loop()
                    # In real code:
                    # addr_infos = await loop.getaddrinfo(hostname, port, ...)

                    # Simulate some failures for demonstration
                    if attempt < 2 and hostname == "unreliable.example.com":
                        raise ConnectionRefusedError("Simulated connection failure")

                    # Connect using Happy Eyeballs
                    # sock = await start_connection(addr_infos)
                    print(f"✓ Connected to {hostname}:{port} on attempt {attempt + 1}")
                    return f"Connected to {hostname}:{port}"

                except Exception as e:
                    print(f"✗ Attempt {attempt + 1} failed: {e}")

                    if attempt < self.max_retries:
                        # Calculate backoff delay: base_delay * (2 ^ attempt) + jitter
                        delay = self.base_delay * (2**attempt)
                        jitter = delay * 0.1  # 10% jitter
                        total_delay = delay + jitter

                        print(f"Retrying in {total_delay:.2f} seconds...")
                        await asyncio.sleep(total_delay)
                    else:
                        print(f"All {self.max_retries + 1} attempts failed")
                        raise

    # Test retry logic
    retry_conn = RetryableConnection(max_retries=3, base_delay=0.5)

    # Test with different scenarios
    test_hosts = [
        ("httpbin.org", 80),  # Should succeed immediately
        ("unreliable.example.com", 80),  # Should fail twice then succeed
    ]

    for host, port in test_hosts:
        try:
            result = await retry_conn.connect_with_retry(host, port)
            print(f"Final result: {result}")
        except Exception as e:
            print(f"Connection ultimately failed: {e}")
        print()


async def main():
    """
    Run all practical usage examples.
    """
    print("aiohappyeyeballs Practical Usage Patterns")
    print("=" * 70)

    examples = [
        dns_cache_with_happy_eyeballs,
        microservice_communication,
        load_balancer_with_health_checks,
        connection_retry_with_backoff,
    ]

    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"Example {example.__name__} failed: {e}")
        print()  # Add spacing between examples

    print("=" * 70)
    print("All practical usage examples completed!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\nExamples interrupted by user")
    except Exception as e:
        print(f"Failed to run examples: {e}")
