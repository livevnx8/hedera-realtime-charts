"""Connection pool example demonstrating health monitoring.

This example demonstrates how to use the WebSocket connection pool
with health monitoring and automatic reconnection.
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from connection_pool import ConnectionPool, ConnectionMonitor


async def message_handler(message: str):
    """Handle incoming WebSocket messages."""
    print(f"Received: {message}")


async def main():
    """Demonstrate connection pool with health monitoring."""
    print("=" * 60)
    print("WebSocket Connection Pool Demo")
    print("=" * 60)
    
    # Create connection pool
    pool = ConnectionPool(max_connections=10, max_retries=5)
    print(f"\nCreated connection pool (max_connections={pool.max_connections})")
    
    # Create connection monitor
    monitor = ConnectionMonitor(pool, check_interval=30)
    print("Created connection monitor (check_interval=30s)")
    
    # Start monitor
    await monitor.start()
    print("Started connection monitor")
    
    # Try to connect (will fail if no WebSocket server running)
    print("\nAttempting to connect to ws://localhost:8000/ws...")
    connected = await pool.connect(
        "ws://localhost:8000/ws",
        message_handler,
        connection_id="demo_connection"
    )
    
    if connected:
        print("✓ Connected successfully")
        
        # Get connection stats
        stats = await pool.get_connection_stats("demo_connection")
        if stats:
            print(f"\nConnection Stats:")
            print(f"  Connected at: {stats.connected_at}")
            print(f"  Messages received: {stats.messages_received}")
            print(f"  Messages sent: {stats.messages_sent}")
            print(f"  Reconnect count: {stats.reconnect_count}")
        
        # Check health
        is_healthy = await pool.check_health("demo_connection")
        print(f"\nConnection health: {'✓ Healthy' if is_healthy else '✗ Unhealthy'}")
        
        # Wait for a bit
        print("\nWaiting 5 seconds...")
        await asyncio.sleep(5)
        
        # Disconnect
        await pool.disconnect("demo_connection")
        print("Disconnected")
    else:
        print("✗ Connection failed (server not running)")
        print("\nTo test with a real server:")
        print("1. Start the server: python -m src.server")
        print("2. Run this example again")
    
    # Stop monitor
    await monitor.stop()
    print("\nStopped connection monitor")
    
    # Close all connections
    await pool.close_all()
    print("Closed all connections")
    
    print("\n" + "=" * 60)
    print("Demo Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
