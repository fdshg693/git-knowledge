"""
Correct Usage Examples for aiohappyeyeballs

This module demonstrates the proper usage patterns of the aiohappyeyeba        # Create local address info for binding
        # Use aiohappyeyeballs utility function
        local_addr_infos = addr_to_addr_infos(("0.0.0.0", 0))

        sock = await start_connection(
            remote_addr_infos,
            local_addr_infos=local_addr_infos
        )ary.
The library provides Happy Eyeballs (RFC 8305) implementation for pre-resolved addresses.

Key Functions:
- start_connection(addr_infos, ...) -> socket
- addr_to_addr_infos(addr) -> list of addr_infos
- remove_addr_infos(addr_infos, addr) -> modified addr_infos
- pop_addr_infos_interleave(addr_infos, num) -> modified addr_infos
"""

import asyncio
import socket
import time

# Import the correct functions from aiohappyeyeballs
from aiohappyeyeballs import (
    start_connection,
    addr_to_addr_infos,
    remove_addr_infos,
    pop_addr_infos_interleave,
)


async def basic_happy_eyeballs_example():
    """
    Demonstrates the core Happy Eyeballs functionality using start_connection.
    """
    print("=== Basic Happy Eyeballs Example ===")

    try:
        # Step 1: Resolve hostname to get address info
        loop = asyncio.get_event_loop()
        addr_infos = await loop.getaddrinfo(
            "httpbin.org",
            80,
            family=socket.AF_UNSPEC,  # Allow both IPv4 and IPv6
            type=socket.SOCK_STREAM,
        )

        print(f"Resolved {len(addr_infos)} addresses:")
        for i, (family, type_, proto, canonname, sockaddr) in enumerate(addr_infos):
            family_name = "IPv6" if family == socket.AF_INET6 else "IPv4"
            print(f"  {i+1}. {family_name}: {sockaddr[0]}:{sockaddr[1]}")

        # Step 2: Use Happy Eyeballs to connect
        start_time = time.time()
        sock = await start_connection(addr_infos)
        connection_time = time.time() - start_time

        # Step 3: Get connection info
        local_addr = sock.getsockname()
        remote_addr = sock.getpeername()

        print(f"Connected in {connection_time:.3f} seconds")
        print(f"Local address: {local_addr}")
        print(f"Remote address: {remote_addr}")
        print(f"Socket family: {'IPv6' if sock.family == socket.AF_INET6 else 'IPv4'}")

        # Step 4: Use the socket (example HTTP request)
        sock.sendall(
            b"GET /ip HTTP/1.1\r\nHost: httpbin.org\r\nConnection: close\r\n\r\n"
        )

        # Receive response (simplified)
        response = sock.recv(1024)
        print(f"Received {len(response)} bytes")

        # Close the socket
        sock.close()
        print("Connection closed successfully")

    except Exception as e:
        print(f"Connection failed: {e}")


async def happy_eyeballs_with_options():
    """
    Demonstrates Happy Eyeballs with custom options and delays.
    """
    print("\\n=== Happy Eyeballs with Options ===")

    try:
        loop = asyncio.get_event_loop()
        addr_infos = await loop.getaddrinfo(
            "httpbin.org", 443, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM
        )

        print(f"Attempting connection to {len(addr_infos)} addresses with custom delay")

        # Custom Happy Eyeballs delay (default is 0.25 seconds)
        sock = await start_connection(
            addr_infos, happy_eyeballs_delay=0.1  # Faster attempts for demo
        )

        print(f"Connected to: {sock.getpeername()}")
        sock.close()

    except Exception as e:
        print(f"Connection with options failed: {e}")


async def local_address_binding_example():
    """
    Shows how to use local address binding with Happy Eyeballs.
    """
    print("\\n=== Local Address Binding Example ===")

    try:
        loop = asyncio.get_event_loop()

        # Resolve remote address
        remote_addr_infos = await loop.getaddrinfo(
            "httpbin.org", 80, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM
        )

        # Create local address info for binding
        # Use aiohappyeyeballs utility function
        local_addr_infos = aiohappyeyeballs.addr_to_addr_infos(("0.0.0.0", 0))

        sock = await aiohappyeyeballs.start_connection(
            remote_addr_infos, local_addr_infos=local_addr_infos
        )

        print(
            f"Connected with local binding: {sock.getsockname()} -> {sock.getpeername()}"
        )
        sock.close()

    except Exception as e:
        print(f"Local binding failed: {e}")


async def address_manipulation_example():
    """
    Demonstrates address manipulation utilities.
    """
    print("\\n=== Address Manipulation Example ===")

    try:
        loop = asyncio.get_event_loop()
        addr_infos = await loop.getaddrinfo(
            "httpbin.org", 80, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM
        )

        print(f"Original address list has {len(addr_infos)} entries")

        # Create a copy for manipulation
        modified_addr_infos = addr_infos.copy()

        # Remove first address of each family (IPv4 and IPv6)
        pop_addr_infos_interleave(modified_addr_infos, 1)
        print(
            f"After popping interleaved addresses: {len(modified_addr_infos)} entries"
        )

        # Try to remove a specific address (if it exists)
        if addr_infos:
            first_addr = addr_infos[0][4][0]  # Get IP address from first entry
            original_count = len(modified_addr_infos)
            remove_addr_infos(modified_addr_infos, first_addr)
            print(
                f"After removing {first_addr}: {len(modified_addr_infos)} entries "
                f"(removed {original_count - len(modified_addr_infos)})"
            )

        # Still try to connect with remaining addresses
        if modified_addr_infos:
            sock = await start_connection(modified_addr_infos)
            print(f"Connected using modified address list: {sock.getpeername()}")
            sock.close()
        else:
            print("No addresses remaining after manipulation")

    except Exception as e:
        print(f"Address manipulation example failed: {e}")


async def error_handling_example():
    """
    Demonstrates error handling scenarios.
    """
    print("\\n=== Error Handling Example ===")

    # Test with unreachable addresses
    try:
        # Create fake address info for unreachable host
        fake_addr_infos = [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                ("192.0.2.1", 12345),
            ),  # RFC5737 test address
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                ("203.0.113.1", 12345),
            ),  # Another test address
        ]

        print("Attempting connection to unreachable addresses...")

        # This should fail quickly
        sock = await asyncio.wait_for(start_connection(fake_addr_infos), timeout=5.0)
        sock.close()
        print("Unexpected success!")

    except asyncio.TimeoutError:
        print("Connection attempt timed out (expected)")
    except OSError as e:
        print(f"Connection failed with OS error (expected): {e}")
    except Exception as e:
        print(f"Connection failed with error: {e}")


async def concurrent_connections_example():
    """
    Shows how to make multiple concurrent connections.
    """
    print("\\n=== Concurrent Connections Example ===")

    async def connect_to_host(hostname, port, connection_id):
        """Helper to connect to a single host."""
        try:
            start_time = time.time()

            loop = asyncio.get_event_loop()
            addr_infos = await loop.getaddrinfo(
                hostname, port, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM
            )

            sock = await start_connection(addr_infos)
            connection_time = time.time() - start_time

            result = {
                "id": connection_id,
                "hostname": hostname,
                "port": port,
                "success": True,
                "time": connection_time,
                "address": sock.getpeername(),
            }

            sock.close()
            return result

        except Exception as e:
            return {
                "id": connection_id,
                "hostname": hostname,
                "port": port,
                "success": False,
                "error": str(e),
                "time": 0,
            }

    # Create multiple connection tasks
    hosts = [
        ("httpbin.org", 80),
        ("httpbin.org", 443),
        ("example.com", 80),
        ("www.google.com", 443),
    ]

    tasks = [connect_to_host(host, port, i + 1) for i, (host, port) in enumerate(hosts)]

    print(f"Starting {len(tasks)} concurrent connections...")
    start_time = time.time()

    results = await asyncio.gather(*tasks, return_exceptions=True)
    total_time = time.time() - start_time

    print(f"All connections completed in {total_time:.3f} seconds")

    for result in results:
        if isinstance(result, dict):
            if result["success"]:
                print(
                    f"  ✓ Connection {result['id']}: {result['hostname']}:{result['port']} "
                    f"-> {result['address']} ({result['time']:.3f}s)"
                )
            else:
                print(
                    f"  ✗ Connection {result['id']}: {result['hostname']}:{result['port']} "
                    f"failed: {result['error']} ({result['time']:.3f}s)"
                )
        else:
            print(f"  ✗ Unexpected result: {result}")


async def main():
    """
    Main function to run all examples.
    """
    print("aiohappyeyeballs Correct Usage Examples")
    print("=" * 60)

    # Check if the library is available
    try:
        import aiohappyeyeballs

        print(
            f"aiohappyeyeballs version: {getattr(aiohappyeyeballs, '__version__', 'unknown')}"
        )
        print(
            f"Available functions: start_connection, addr_to_addr_infos, remove_addr_infos, pop_addr_infos_interleave"
        )
    except ImportError:
        print("Could not import aiohappyeyeballs - please install it first")

    print()

    # Run all examples
    examples = [
        basic_happy_eyeballs_example,
        happy_eyeballs_with_options,
        local_address_binding_example,
        address_manipulation_example,
        error_handling_example,
        concurrent_connections_example,
    ]

    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"Example {example.__name__} failed: {e}")
        print()  # Add spacing between examples

    print("=" * 60)
    print("All examples completed!")


if __name__ == "__main__":
    # Run the examples
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\nExamples interrupted by user")
    except Exception as e:
        print(f"Failed to run examples: {e}")
