# aiohappyeyeballs: Advanced Dual-Stack Networking in Python

## Overview

`aiohappyeyeballs` is a Python library that implements RFC 8305 (Happy Eyeballs Version 2) for asyncio applications. It provides intelligent connection handling for dual-stack networks (IPv4 and IPv6), ensuring optimal connectivity by attempting connections to multiple IP addresses simultaneously and selecting the fastest successful connection.

## What is Happy Eyeballs?

Happy Eyeballs is a networking algorithm designed to improve user experience when connecting to servers that support both IPv4 and IPv6. Instead of waiting for one protocol to fail before trying another, it attempts connections concurrently and uses the first successful connection.

### Key Benefits
- **Faster Connection Times**: Reduces connection latency by testing multiple addresses simultaneously
- **Better Reliability**: Gracefully handles IPv6/IPv4 connectivity issues
- **Improved User Experience**: Eliminates connection timeouts when one protocol is unavailable
- **Standards Compliant**: Implements RFC 8305 specifications

## Core Concepts

### 1. Dual-Stack Networking
Modern networks support both IPv4 and IPv6 protocols. Traditional connection attempts test these sequentially, which can cause delays if the preferred protocol fails.

### 2. Connection Racing
The library "races" multiple connection attempts, selecting the first successful connection and canceling others.

### 3. Address Sorting
Implements intelligent address sorting based on RFC 3484 and RFC 6724, prioritizing IPv6 over IPv4 when appropriate.

## Installation

```bash
pip install aiohappyeyeballs
```

## Basic Usage

### Simple Connection Example

```python
import asyncio
import socket
from aiohappyeyeballs import start_connection

async def connect_to_host():
    # First, resolve the hostname to get address info
    loop = asyncio.get_event_loop()
    addr_infos = await loop.getaddrinfo(
        'example.com', 80,
        family=socket.AF_UNSPEC,  # Allow both IPv4 and IPv6
        type=socket.SOCK_STREAM
    )
    
    # Use aiohappyeyeballs to connect with Happy Eyeballs algorithm
    sock = await start_connection(addr_infos)
    
    # Create transport and protocol using the socket
    transport, protocol = await loop.create_connection(
        lambda: asyncio.Protocol(),
        sock=sock
    )
    
    # Use the connection...
    transport.close()

# Run the example
asyncio.run(connect_to_host())
```

## Advanced Features

### 1. Custom Socket Options

```python
import socket
from aiohappyeyeballs import start_connection

async def connect_with_options():
    # First resolve the address
    loop = asyncio.get_event_loop()
    addr_infos = await loop.getaddrinfo(
        'api.example.com', 443,
        family=socket.AF_UNSPEC,
        type=socket.SOCK_STREAM
    )
    
    # Define custom socket factory with options
    def socket_factory(addr_info):
        family, type_, proto, _, _ = addr_info
        sock = socket.socket(family=family, type=type_, proto=proto)
        
        # Apply socket options
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        return sock
    
    sock = await start_connection(
        addr_infos,
        socket_factory=socket_factory
    )
```

### 2. Custom Address Resolution

```python
from aiohappyeyeballs import start_connection, addr_to_addr_infos

async def connect_with_custom_resolution():
    # Provide custom addresses to avoid DNS lookup
    # Note: addr_to_addr_infos is a utility function
    custom_addresses = [
        (socket.AF_INET6, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', ('2001:db8::1', 80, 0, 0)),
        (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', ('192.0.2.1', 80))
    ]
    
    sock = await start_connection(custom_addresses)
```

### 3. Connection Timing Control

```python
from aiohappyeyeballs import start_connection

async def connect_with_timing():
    loop = asyncio.get_event_loop()
    addr_infos = await loop.getaddrinfo(
        'slow-server.com', 80,
        family=socket.AF_UNSPEC,
        type=socket.SOCK_STREAM
    )
    
    sock = await start_connection(
        addr_infos,
        happy_eyeballs_delay=0.25  # Delay between connection attempts
    )
```

## Real-World Applications

### 1. HTTP Client with Fallback
Implementing a robust HTTP client that handles connectivity issues gracefully.

### 2. Database Connections
Ensuring reliable database connections in mixed IPv4/IPv6 environments.

### 3. Microservices Communication
Improving service-to-service communication reliability in containerized environments.

### 4. IoT Device Communication
Handling connectivity in environments where network protocols may be inconsistent.

## Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `addr_infos` | Required | Sequence of address info tuples from getaddrinfo() |
| `local_addr_infos` | None | Local addresses to bind to |
| `happy_eyeballs_delay` | 0.25 | Delay (seconds) between connection attempts |
| `interleave` | None | Number of addresses to interleave by family |
| `loop` | None | Event loop to use (defaults to current loop) |
| `socket_factory` | None | Custom function to create sockets |

## Error Handling

### Common Exception Types

```python
import asyncio
import socket
from aiohappyeyeballs import start_connection

async def handle_connection_errors():
    try:
        # Resolve addresses
        loop = asyncio.get_event_loop()
        addr_infos = await loop.getaddrinfo(
            'unreachable.example.com', 80,
            family=socket.AF_UNSPEC,
            type=socket.SOCK_STREAM
        )
        
        sock = await start_connection(addr_infos)
        sock.close()
        
    except socket.gaierror as e:
        print(f"DNS resolution failed: {e}")
    except OSError as e:
        print(f"Connection failed: {e}")
    except asyncio.TimeoutError:
        print("Connection timed out")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

## Best Practices

### 1. Timeout Configuration
Always consider using asyncio.wait_for() for overall timeout control:

```python
# Good: Set reasonable timeouts
try:
    sock = await asyncio.wait_for(
        start_connection(addr_infos),
        timeout=10.0
    )
except asyncio.TimeoutError:
    print("Connection timed out")
```

### 2. Resource Management
Always close sockets properly:

```python
async def proper_resource_management():
    loop = asyncio.get_event_loop()
    addr_infos = await loop.getaddrinfo(
        'example.com', 80,
        family=socket.AF_UNSPEC,
        type=socket.SOCK_STREAM
    )
    
    sock = await start_connection(addr_infos)
    
    try:
        # Use socket
        transport, protocol = await loop.create_connection(
            lambda: asyncio.Protocol(),
            sock=sock
        )
        # Do work...
    finally:
        # Socket is managed by transport, which will close it
        transport.close()
```

### 3. Connection Pooling
For applications making many connections, consider implementing connection pooling:

```python
import asyncio
from asyncio import Queue

class ConnectionPool:
    def __init__(self, host, port, max_connections=10):
        self.host = host
        self.port = port
        self.pool = Queue(maxsize=max_connections)
        self.created_connections = 0
        self.max_connections = max_connections
    
    async def get_connection(self):
        if not self.pool.empty():
            return await self.pool.get()
        
        if self.created_connections < self.max_connections:
            reader, writer = await aiohappyeyeballs.open_connection(
                self.host, self.port
            )
            self.created_connections += 1
            return reader, writer
        
        return await self.pool.get()
    
    async def return_connection(self, reader, writer):
        await self.pool.put((reader, writer))
```

## Performance Considerations

### 1. Connection Delay Tuning
The `happy_eyeballs_delay` parameter affects connection performance:
- **Lower values (0.1-0.2s)**: Faster for reliable networks
- **Higher values (0.3-0.5s)**: Better for unreliable networks

### 2. DNS Resolution
Pre-resolving addresses can improve performance:

```python
import socket

# Pre-resolve addresses
addresses = []
for family, type, proto, canonname, sockaddr in socket.getaddrinfo(
    'example.com', 80, socket.AF_UNSPEC, socket.SOCK_STREAM
):
    addresses.append(sockaddr)

# Use pre-resolved addresses
reader, writer = await aiohappyeyeballs.open_connection(
    host=None,
    port=None,
    addresses=addresses
)
```

## Common Pitfalls and Solutions

### 1. IPv6 Not Available
**Problem**: Application fails when IPv6 is not available
**Solution**: Let aiohappyeyeballs handle fallback automatically

### 2. Long Connection Times
**Problem**: Connections take too long to establish
**Solution**: Tune `happy_eyeballs_delay` and `sock_connect_timeout`

### 3. Resource Leaks
**Problem**: Connections not properly closed
**Solution**: Always use try/finally blocks or async context managers

## Integration with Popular Libraries

### Custom HTTP Client Integration
```python
import aiohttp
import socket
from aiohappyeyeballs import start_connection

class HappyEyeballsConnector(aiohttp.TCPConnector):
    """Custom connector using aiohappyeyeballs."""
    
    async def _create_connection(self, req, traces, timeout):
        # Resolve hostname
        host, port = req.host, req.port or (443 if req.is_ssl() else 80)
        
        addr_infos = await self._loop.getaddrinfo(
            host, port,
            family=socket.AF_UNSPEC,
            type=socket.SOCK_STREAM
        )
        
        # Use Happy Eyeballs for connection
        sock = await start_connection(addr_infos)
        
        # Create the connection
        return aiohttp.TCPTransport(self._loop, sock, req.url.host)

# Usage
async def use_custom_connector():
    connector = HappyEyeballsConnector()
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get('https://api.example.com') as response:
            data = await response.json()
```

### With asyncio-mqtt
```python
import asyncio_mqtt
import aiohappyeyeballs

# Use with MQTT client for better connectivity
async def mqtt_with_happy_eyeballs():
    try:
        # aiohappyeyeballs is used internally by asyncio-mqtt
        # when available, improving connection reliability
        async with asyncio_mqtt.Client("mqtt.example.com") as client:
            await client.subscribe("sensors/temperature")
            async with client.messages() as messages:
                async for message in messages:
                    print(f"Received: {message.payload.decode()}")
    except Exception as e:
        print(f"MQTT connection failed: {e}")
```

## Conclusion

`aiohappyeyeballs` is an essential library for modern Python applications that need robust networking capabilities. By implementing the Happy Eyeballs algorithm, it significantly improves connection reliability and performance in dual-stack environments. The library's integration with asyncio makes it a natural choice for async Python applications requiring optimal network connectivity.

### Key Takeaways
- Use aiohappyeyeballs for applications requiring reliable network connections
- Configure timeouts appropriately for your use case
- Take advantage of the library's automatic IPv4/IPv6 fallback
- Implement proper error handling and resource management
- Consider performance implications when tuning connection parameters
