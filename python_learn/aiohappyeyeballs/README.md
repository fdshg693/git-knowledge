# aiohappyeyeballs Learning Resources

This directory contains comprehensive learning materials for the `aiohappyeyeballs` Python library, which implements Happy Eyeballs (RFC 8305) for asyncio applications.

## What is aiohappyeyeballs?

`aiohappyeyeballs` is a Python library that provides intelligent dual-stack networking for asyncio applications. It implements the Happy Eyeballs algorithm to improve connection reliability and performance when connecting to servers that support both IPv4 and IPv6.

### Key Benefits
- **Faster Connections**: Attempts multiple addresses simultaneously
- **Better Reliability**: Graceful IPv4/IPv6 fallback
- **Standards Compliant**: Implements RFC 8305
- **Pre-resolved Addresses**: Works with cached DNS results

## Directory Structure

```
aiohappyeyeballs/
├── output/
│   └── aiohappyeyeballs_guide.md    # Comprehensive documentation
├── examples/
│   ├── correct_usage.py             # Basic usage examples
│   ├── advanced_integration.py      # Integration patterns
│   └── practical_patterns.py        # Real-world use cases
└── README.md                        # This file
```

## Getting Started

### Installation
```bash
pip install aiohappyeyeballs
```

### Basic Usage
```python
import asyncio
import socket
from aiohappyeyeballs import start_connection

async def connect_example():
    # Resolve hostname first
    loop = asyncio.get_event_loop()
    addr_infos = await loop.getaddrinfo(
        'example.com', 80,
        family=socket.AF_UNSPEC,
        type=socket.SOCK_STREAM
    )
    
    # Connect using Happy Eyeballs
    sock = await start_connection(addr_infos)
    
    # Use the socket...
    sock.close()

asyncio.run(connect_example())
```

## Core Concepts

### 1. Happy Eyeballs Algorithm
- Attempts connections to multiple IP addresses simultaneously
- Uses the first successful connection
- Implements intelligent delays between attempts

### 2. Pre-resolved Addresses
- Works with `getaddrinfo()` results
- Ideal for DNS caching scenarios
- Better control over address selection

### 3. Dual-Stack Support
- Handles both IPv4 and IPv6 addresses
- Automatic fallback between protocols
- Address family interleaving

## Key Functions

### `start_connection(addr_infos, **kwargs)`
Main function to establish connections using Happy Eyeballs.

**Parameters:**
- `addr_infos`: Sequence of address info tuples from `getaddrinfo()`
- `local_addr_infos`: Optional local addresses to bind to
- `happy_eyeballs_delay`: Delay between connection attempts (default: 0.25s)
- `interleave`: Number of addresses to interleave by family
- `socket_factory`: Custom socket creation function

### Utility Functions
- `addr_to_addr_infos(addr)`: Convert address tuple to addr_info format
- `remove_addr_infos(addr_infos, addr)`: Remove specific address from list
- `pop_addr_infos_interleave(addr_infos, num)`: Remove addresses by family

## Learning Path

### 1. Start with Documentation
Read `output/aiohappyeyeballs_guide.md` for comprehensive understanding.

### 2. Basic Examples
Run `examples/correct_usage.py` to see fundamental usage patterns.

### 3. Advanced Integration
Explore `examples/advanced_integration.py` for library integration.

### 4. Real-world Patterns
Study `examples/practical_patterns.py` for production scenarios.

## Common Use Cases

### DNS Caching
```python
# Cache DNS results and use Happy Eyeballs for connections
addr_infos = dns_cache.get('example.com:80')
sock = await start_connection(addr_infos)
```

### Microservices
```python
# Service discovery with multiple endpoints
endpoints = service_discovery.get_endpoints('user-service')
sock = await start_connection(endpoints)
```

### Load Balancing
```python
# Connect to first available backend
backend_addrs = await get_healthy_backends()
sock = await start_connection(backend_addrs)
```

### Connection Pooling
```python
# Create optimized connections for pools
def socket_factory(addr_info):
    sock = socket.socket(...)
    # Apply optimizations
    return sock

sock = await start_connection(addr_infos, socket_factory=socket_factory)
```

## Best Practices

1. **Always resolve addresses first** using `getaddrinfo()`
2. **Handle exceptions** appropriately (OSError, socket.gaierror)
3. **Use timeouts** with `asyncio.wait_for()`
4. **Close sockets** properly in finally blocks
5. **Consider local binding** for multi-homed hosts
6. **Tune delays** based on network conditions

## Error Handling

Common exceptions to handle:
- `socket.gaierror`: DNS resolution failures
- `OSError`: Connection failures
- `asyncio.TimeoutError`: Connection timeouts
- `RuntimeError`: Event loop issues

## Performance Considerations

- **Happy Eyeballs Delay**: Tune based on network reliability
- **Address Ordering**: IPv6 typically preferred over IPv4
- **DNS Caching**: Pre-resolve addresses when possible
- **Connection Pooling**: Reuse connections for efficiency

## Integration Examples

The library works well with:
- **aiohttp**: Custom connectors for HTTP clients
- **asyncio servers**: Outbound connections from servers
- **Database clients**: Reliable database connections
- **Microservice frameworks**: Service-to-service communication

## Troubleshooting

### Import Errors
Ensure aiohappyeyeballs is installed: `pip install aiohappyeyeballs`

### Connection Failures
- Check DNS resolution with `getaddrinfo()`
- Verify network connectivity
- Consider firewall rules
- Test with individual addresses

### Performance Issues
- Tune `happy_eyeballs_delay` parameter
- Check for DNS resolution delays
- Monitor connection establishment times
- Consider local address binding

## Additional Resources

- [RFC 8305 - Happy Eyeballs Version 2](https://www.rfc-editor.org/rfc/rfc8305.html)
- [GitHub Repository](https://github.com/aio-libs/aiohappyeyeballs)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [Socket Programming Guide](https://docs.python.org/3/library/socket.html)

## Contributing

When working with these examples:
1. Install aiohappyeyeballs: `pip install aiohappyeyeballs`
2. Run examples to see the library in action
3. Modify examples to experiment with different scenarios
4. Test with various network conditions

The examples are designed to be educational and demonstrate both basic usage and advanced patterns for real-world applications.
