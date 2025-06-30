"""
Advanced Integration Examples for aiohappyeyeballs

This module demonstrates how to integrate aiohappyeyeballs with popular libraries
and frameworks for real-world applications.
"""

import asyncio
import socket
import ssl
import time
from typing import Optional, Tuple

# Import aiohappyeyeballs functions
from aiohappyeyeballs import start_connection, addr_to_addr_infos  # type: ignore


class HappyEyeballsHTTPClient:
    """
    A simple HTTP client that uses aiohappyeyeballs for connection establishment.
    """

    def __init__(self, happy_eyeballs_delay: float = 0.25):
        self.happy_eyeballs_delay = happy_eyeballs_delay

    async def get(
        self, url: str, headers: Optional[dict] = None
    ) -> Tuple[int, dict, bytes]:
        """
        Perform an HTTP GET request using Happy Eyeballs for connection.

        Returns:
            Tuple of (status_code, headers_dict, response_body)
        """
        # Parse URL (simple implementation)
        if url.startswith("https://"):
            host = url[8:].split("/")[0]
            path = "/" + "/".join(url[8:].split("/")[1:]) if "/" in url[8:] else "/"
            port = 443
            use_ssl = True
        elif url.startswith("http://"):
            host = url[7:].split("/")[0]
            path = "/" + "/".join(url[7:].split("/")[1:]) if "/" in url[7:] else "/"
            port = 80
            use_ssl = False
        else:
            raise ValueError("URL must start with http:// or https://")

        # Handle port in hostname
        if ":" in host:
            host, port_str = host.split(":")
            port = int(port_str)

        # Resolve hostname
        loop = asyncio.get_event_loop()
        addr_infos = await loop.getaddrinfo(
            host, port, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM
        )

        # Connect using Happy Eyeballs
        sock = await start_connection(
            addr_infos, happy_eyeballs_delay=self.happy_eyeballs_delay
        )

        try:
            # Wrap in SSL if needed
            if use_ssl:
                ssl_context = ssl.create_default_context()
                sock = ssl_context.wrap_socket(sock, server_hostname=host)

            # Build HTTP request
            request_headers = headers or {}
            request_headers.setdefault("Host", host)
            request_headers.setdefault("User-Agent", "HappyEyeballsHTTPClient/1.0")
            request_headers.setdefault("Connection", "close")

            request_lines = [f"GET {path} HTTP/1.1"]
            for key, value in request_headers.items():
                request_lines.append(f"{key}: {value}")
            request_lines.append("")  # Empty line to end headers
            request_lines.append("")  # Empty line to end request

            request = "\\r\\n".join(request_lines).encode()

            # Send request
            sock.sendall(request)

            # Read response
            response = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
                # For simplicity, we'll read until connection closes
                # In a real implementation, you'd parse Content-Length, etc.

            # Parse response (simplified)
            response_text = response.decode("utf-8", errors="ignore")
            lines = response_text.split("\\r\\n")

            # Parse status line
            status_line = lines[0]
            status_code = int(status_line.split()[1])

            # Parse headers
            response_headers = {}
            header_end_idx = 0
            for i, line in enumerate(lines[1:], 1):
                if not line:
                    header_end_idx = i + 1
                    break
                if ":" in line:
                    key, value = line.split(":", 1)
                    response_headers[key.strip()] = value.strip()

            # Get body
            body_lines = lines[header_end_idx:]
            body = "\\r\\n".join(body_lines).encode()

            return status_code, response_headers, body

        finally:
            sock.close()


async def http_client_example():
    """
    Demonstrate the custom HTTP client with Happy Eyeballs.
    """
    print("=== HTTP Client with Happy Eyeballs Example ===")

    client = HappyEyeballsHTTPClient(happy_eyeballs_delay=0.2)

    try:
        start_time = time.time()
        status_code, headers, body = await client.get("http://httpbin.org/ip")
        request_time = time.time() - start_time

        print(f"Response received in {request_time:.3f} seconds")
        print(f"Status code: {status_code}")
        print(f"Headers: {dict(list(headers.items())[:3])}...")  # Show first 3 headers
        print(f"Body preview: {body[:100].decode(errors='ignore')}...")

    except Exception as e:
        print(f"HTTP request failed: {e}")


async def tcp_server_with_happy_eyeballs():
    """
    Example of a TCP server that uses Happy Eyeballs for outbound connections.
    This simulates a proxy or gateway service.
    """
    print("\\n=== TCP Server with Happy Eyeballs Example ===")

    class HappyEyeballsProxy:
        def __init__(self):
            self.connection_count = 0

        async def handle_client(self, reader, writer):
            """Handle incoming client connections."""
            self.connection_count += 1
            client_addr = writer.get_extra_info("peername")
            print(f"Connection #{self.connection_count} from {client_addr}")

            try:
                # Read target from client (simplified protocol)
                target_line = await reader.readline()
                target = target_line.decode().strip()

                if not target:
                    writer.write(b"ERROR: No target specified\\n")
                    return

                # Parse target
                try:
                    host, port = target.split(":")
                    port = int(port)
                except ValueError:
                    writer.write(b"ERROR: Invalid target format (use host:port)\\n")
                    return

                print(f"  Connecting to {host}:{port} using Happy Eyeballs...")

                # Resolve and connect using Happy Eyeballs
                loop = asyncio.get_event_loop()
                addr_infos = await loop.getaddrinfo(
                    host, port, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM
                )

                target_sock = await start_connection(addr_infos)
                print(f"  Connected to {target_sock.getpeername()}")

                # Send success response
                writer.write(f"CONNECTED to {host}:{port}\\n".encode())
                await writer.drain()

                # Clean up
                target_sock.close()

            except Exception as e:
                error_msg = f"ERROR: {e}\\n"
                writer.write(error_msg.encode())
                print(f"  Connection failed: {e}")

            finally:
                writer.close()
                await writer.wait_closed()
                print(f"  Connection #{self.connection_count} closed")

    # Create and start the proxy server
    proxy = HappyEyeballsProxy()

    # Start server on localhost:8888
    server = await asyncio.start_server(proxy.handle_client, "127.0.0.1", 8888)

    print("Proxy server started on 127.0.0.1:8888")
    print("Send 'host:port' to test connections (e.g., 'httpbin.org:80')")

    # Run server for a short time for demo
    try:
        await asyncio.wait_for(server.wait_closed(), timeout=2.0)
    except asyncio.TimeoutError:
        print("Demo timeout - stopping server")
        server.close()
        await server.wait_closed()


async def connection_pool_example():
    """
    Demonstrate a simple connection pool using Happy Eyeballs.
    """
    print("\\n=== Connection Pool with Happy Eyeballs Example ===")

    class HappyEyeballsConnectionPool:
        def __init__(self, host: str, port: int, max_connections: int = 5):
            self.host = host
            self.port = port
            self.max_connections = max_connections
            self.available_connections = asyncio.Queue()
            self.active_connections = 0
            self.total_created = 0

        async def get_connection(self):
            """Get a connection from the pool."""
            # Try to get an existing connection
            try:
                sock = self.available_connections.get_nowait()
                print(f"Reusing existing connection")
                return sock
            except asyncio.QueueEmpty:
                pass

            # Create new connection if under limit
            if self.active_connections < self.max_connections:
                return await self._create_connection()

            # Wait for an available connection
            print("Waiting for available connection...")
            return await self.available_connections.get()

        async def _create_connection(self):
            """Create a new connection using Happy Eyeballs."""
            loop = asyncio.get_event_loop()
            addr_infos = await loop.getaddrinfo(
                self.host, self.port, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM
            )

            sock = await start_connection(addr_infos)
            self.active_connections += 1
            self.total_created += 1

            print(
                f"Created new connection #{self.total_created} to {sock.getpeername()}"
            )
            return sock

        async def return_connection(self, sock):
            """Return a connection to the pool."""
            # In a real implementation, you'd check if the connection is still valid
            try:
                # Simple check - try to get socket info
                sock.getpeername()
                await self.available_connections.put(sock)
                print("Connection returned to pool")
            except (OSError, AttributeError):
                # Connection is bad, close it
                try:
                    sock.close()
                except:
                    pass
                self.active_connections -= 1
                print("Bad connection discarded")

        async def close_all(self):
            """Close all connections in the pool."""
            closed_count = 0
            while not self.available_connections.empty():
                try:
                    sock = self.available_connections.get_nowait()
                    sock.close()
                    closed_count += 1
                except:
                    break

            print(f"Closed {closed_count} pooled connections")

    # Demonstrate the connection pool
    pool = HappyEyeballsConnectionPool("httpbin.org", 80, max_connections=3)

    async def use_connection(connection_id: int):
        """Use a connection from the pool."""
        sock = await pool.get_connection()
        try:
            # Simulate some work
            print(f"Connection {connection_id} using {sock.getpeername()}")
            await asyncio.sleep(0.1)

            # Do a simple HTTP request
            request = b"GET /ip HTTP/1.1\\r\\nHost: httpbin.org\\r\\nConnection: keep-alive\\r\\n\\r\\n"
            sock.sendall(request)

            # Read some response
            response = sock.recv(1024)
            print(f"Connection {connection_id} got {len(response)} bytes")

        finally:
            await pool.return_connection(sock)

    # Create multiple tasks to test the pool
    tasks = [use_connection(i) for i in range(5)]
    await asyncio.gather(*tasks)

    # Clean up
    await pool.close_all()


async def custom_socket_factory_example():
    """
    Demonstrate using a custom socket factory with aiohappyeyeballs.
    """
    print("\\n=== Custom Socket Factory Example ===")

    def optimized_socket_factory(addr_info):
        """
        Create a socket with custom optimizations.
        """
        family, type_, proto, _, _ = addr_info
        sock = socket.socket(family=family, type=type_, proto=proto)

        # Apply optimizations
        if family == socket.AF_INET or family == socket.AF_INET6:
            # Enable TCP keepalive
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

            # Disable Nagle's algorithm for low latency
            if proto == socket.IPPROTO_TCP:
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

            # Set socket buffer sizes
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 64 * 1024)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 64 * 1024)

        print(f"Created optimized socket for {family} family")
        return sock

    try:
        # Resolve target
        loop = asyncio.get_event_loop()
        addr_infos = await loop.getaddrinfo(
            "httpbin.org", 80, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM
        )

        # Connect using custom socket factory
        sock = await start_connection(
            addr_infos, socket_factory=optimized_socket_factory
        )

        print(f"Connected with optimized socket: {sock.getpeername()}")

        # Test the connection
        request = b"GET /headers HTTP/1.1\\r\\nHost: httpbin.org\\r\\nConnection: close\\r\\n\\r\\n"
        sock.sendall(request)

        response = sock.recv(2048)
        print(f"Received response: {len(response)} bytes")

        sock.close()

    except Exception as e:
        print(f"Custom socket factory example failed: {e}")


async def main():
    """
    Run all advanced integration examples.
    """
    print("aiohappyeyeballs Advanced Integration Examples")
    print("=" * 70)

    examples = [
        http_client_example,
        tcp_server_with_happy_eyeballs,
        connection_pool_example,
        custom_socket_factory_example,
    ]

    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"Example {example.__name__} failed: {e}")
        print()  # Add spacing between examples

    print("=" * 70)
    print("All advanced examples completed!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\nExamples interrupted by user")
    except Exception as e:
        print(f"Failed to run examples: {e}")
