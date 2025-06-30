"""
Basic Usage Examples for aiohappyeyeballs

This module demonstrates fundamental usage patterns of the aiohappyeyeballs library
for establishing network connections with automatic IPv4/IPv6 fallback.

Note: aiohappyeyeballs works with pre-resolved addresses, not hostnames directly.
"""

import asyncio
import aiohappyeyeballs
import socket
import time


async def basic_connection_example():
    """
    Demonstrates the basic way to establish a connection using aiohappyeyeballs.
    This library works with pre-resolved addresses from getaddrinfo().
    """
    print("=== Basic Connection Example ===")

    try:
        # First, resolve the hostname to get address info
        loop = asyncio.get_event_loop()
        addr_infos = await loop.getaddrinfo(
            "httpbin.org", 80, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM
        )

        print(f"Resolved {len(addr_infos)} addresses for httpbin.org:80")
        for i, addr_info in enumerate(addr_infos):
            family, type_, proto, canonname, sockaddr = addr_info
            family_name = "IPv6" if family == socket.AF_INET6 else "IPv4"
            print(f"  {i+1}. {family_name}: {sockaddr[0]}:{sockaddr[1]}")

        # Use aiohappyeyeballs to connect with Happy Eyeballs algorithm
        sock = await aiohappyeyeballs.start_connection(addr_infos)

        print(f"Connected using socket: {sock.getpeername()}")

        # Create a transport and protocol using the socket
        transport, protocol = await loop.create_connection(
            lambda: asyncio.Protocol(), sock=sock
        )

        # Send a simple HTTP request
        request = b"GET /ip HTTP/1.1\r\nHost: httpbin.org\r\nConnection: close\r\n\r\n"
        transport.write(request)

        # Allow some time for response (simplified example)
        await asyncio.sleep(1)

        print("Request sent successfully")
        transport.close()

    except Exception as e:
        print(f"Connection failed: {e}")


async def https_connection_example():
    """
    Demonstrates establishing secure HTTPS connections with SSL support.
    """
    print("\\n=== HTTPS Connection Example ===")

    try:
        # HTTPS connection with SSL
        reader, writer = await aiohappyeyeballs.open_connection(
            host="httpbin.org",
            port=443,
            ssl=True,  # Enable SSL/TLS
            server_hostname="httpbin.org",  # For proper certificate validation
        )

        # Send HTTPS request
        request = (
            b"GET /json HTTP/1.1\r\nHost: httpbin.org\r\nConnection: close\r\n\r\n"
        )
        writer.write(request)
        await writer.drain()

        # Read response headers
        headers = []
        while True:
            line = await reader.readline()
            if line == b"\\r\\n":
                break
            headers.append(line.decode().strip())

        print("HTTPS connection established successfully")
        print(f"Received {len(headers)} header lines")
        print(f"Status: {headers[0] if headers else 'No headers'}")

        writer.close()
        await writer.wait_closed()

    except Exception as e:
        print(f"HTTPS connection failed: {e}")


async def timeout_configuration_example():
    """
    Shows how to configure timeouts for connection attempts.
    """
    print("\\n=== Timeout Configuration Example ===")

    # Test with a reasonable timeout
    start_time = time.time()

    try:
        reader, writer = await aiohappyeyeballs.open_connection(
            host="httpbin.org",
            port=80,
            sock_connect_timeout=5.0,  # 5-second timeout per socket
            happy_eyeballs_delay=0.2,  # 200ms delay between attempts
        )

        connection_time = time.time() - start_time
        print(f"Connection established in {connection_time:.3f} seconds")

        writer.close()
        await writer.wait_closed()

    except asyncio.TimeoutError:
        print("Connection timed out")
    except Exception as e:
        print(f"Connection failed: {e}")


async def socket_options_example():
    """
    Demonstrates how to set custom socket options for connections.
    """
    print("\\n=== Socket Options Example ===")

    # Define socket options for optimization
    sock_opts = [
        (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),  # Enable keepalive
        (socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),  # Disable Nagle algorithm
        (socket.SOL_SOCKET, socket.SO_REUSEADDR, 1),  # Allow address reuse
    ]

    try:
        reader, writer = await aiohappyeyeballs.open_connection(
            host="httpbin.org", port=80, sock_opts=sock_opts
        )

        # Get socket information
        sock = writer.get_extra_info("socket")
        if sock:
            print(f"Socket family: {sock.family}")
            print(f"Socket type: {sock.type}")
            print(f"Local address: {sock.getsockname()}")
            print(f"Remote address: {sock.getpeername()}")

        writer.close()
        await writer.wait_closed()
        print("Socket options applied successfully")

    except Exception as e:
        print(f"Failed to apply socket options: {e}")


async def error_handling_example():
    """
    Demonstrates proper error handling for various failure scenarios.
    """
    print("\\n=== Error Handling Example ===")

    # List of hosts to test (some may fail)
    test_hosts = [
        ("httpbin.org", 80),  # Should succeed
        ("nonexistent.invalid", 80),  # DNS failure
        ("httpbin.org", 12345),  # Connection refused
    ]

    for host, port in test_hosts:
        print(f"\\nTesting connection to {host}:{port}")

        try:
            reader, writer = await aiohappyeyeballs.open_connection(
                host=host, port=port, sock_connect_timeout=3.0
            )

            print(f"✓ Successfully connected to {host}:{port}")
            writer.close()
            await writer.wait_closed()

        except socket.gaierror as e:
            print(f"✗ DNS resolution failed for {host}: {e}")
        except ConnectionRefusedError as e:
            print(f"✗ Connection refused to {host}:{port}: {e}")
        except asyncio.TimeoutError:
            print(f"✗ Connection to {host}:{port} timed out")
        except OSError as e:
            print(f"✗ OS error connecting to {host}:{port}: {e}")
        except Exception as e:
            print(f"✗ Unexpected error connecting to {host}:{port}: {e}")


async def concurrent_connections_example():
    """
    Shows how to make multiple concurrent connections efficiently.
    """
    print("\\n=== Concurrent Connections Example ===")

    async def make_connection(host, port, connection_id):
        """Helper function to make a single connection."""
        try:
            start_time = time.time()
            reader, writer = await aiohappyeyeballs.open_connection(
                host=host, port=port, sock_connect_timeout=5.0
            )

            connection_time = time.time() - start_time
            print(
                f"Connection {connection_id}: {host}:{port} - "
                f"Connected in {connection_time:.3f}s"
            )

            writer.close()
            await writer.wait_closed()
            return f"Connection {connection_id} successful"

        except Exception as e:
            print(f"Connection {connection_id}: {host}:{port} - Failed: {e}")
            return f"Connection {connection_id} failed"

    # Make multiple concurrent connections
    connection_tasks = [
        make_connection("httpbin.org", 80, 1),
        make_connection("httpbin.org", 443, 2),
        make_connection("example.com", 80, 3),
        make_connection("google.com", 443, 4),
    ]

    start_time = time.time()
    results = await asyncio.gather(*connection_tasks, return_exceptions=True)
    total_time = time.time() - start_time

    print(f"\\nAll connections completed in {total_time:.3f} seconds")
    for result in results:
        print(f"Result: {result}")


async def main():
    """
    Main function to run all examples.
    """
    print("aiohappyeyeballs Basic Usage Examples")
    print("=" * 50)

    # Run all examples
    await basic_connection_example()
    await https_connection_example()
    await timeout_configuration_example()
    await socket_options_example()
    await error_handling_example()
    await concurrent_connections_example()

    print("\\n" + "=" * 50)
    print("All examples completed!")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())
