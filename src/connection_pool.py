"""WebSocket connection pool with health monitoring."""

import asyncio
import websockets
import time
import logging
from typing import Dict, Set, Optional, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """WebSocket connection state."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


@dataclass
class ConnectionStats:
    """Connection statistics."""
    connected_at: float
    messages_received: int
    messages_sent: int
    last_message_time: float
    reconnect_count: int
    latency_ms: float


class ConnectionPool:
    """Pool of WebSocket connections with health monitoring."""
    
    def __init__(self, max_connections: int = 10, max_retries: int = 5):
        self.max_connections = max_connections
        self.max_retries = max_retries
        self.connections: Dict[str, websockets.WebSocketClientProtocol] = {}
        self.connection_states: Dict[str, ConnectionState] = {}
        self.connection_stats: Dict[str, ConnectionStats] = {}
        self.callbacks: Dict[str, Callable] = {}
        self.lock = asyncio.Lock()
        
    async def connect(self, url: str, callback: Callable, connection_id: str = None) -> bool:
        """
        Connect to a WebSocket with health monitoring.
        
        Args:
            url: WebSocket URL
            callback: Callback function for messages
            connection_id: Unique identifier for connection
            
        Returns:
            True if connected successfully
        """
        if connection_id is None:
            connection_id = url
            
        async with self.lock:
            if connection_id in self.connections:
                logger.warning(f"Connection {connection_id} already exists")
                return True
            
            self.connection_states[connection_id] = ConnectionState.CONNECTING
            
        try:
            websocket = await websockets.connect(
                url,
                ping_interval=20,
                ping_timeout=20,
                close_timeout=1,
            )
            
            async with self.lock:
                self.connections[connection_id] = websocket
                self.connection_states[connection_id] = ConnectionState.CONNECTED
                self.callbacks[connection_id] = callback
                self.connection_stats[connection_id] = ConnectionStats(
                    connected_at=time.time(),
                    messages_received=0,
                    messages_sent=0,
                    last_message_time=time.time(),
                    reconnect_count=0,
                    latency_ms=0
                )
            
            logger.info(f"Connected to {connection_id}")
            return True
            
        except Exception as e:
            async with self.lock:
                self.connection_states[connection_id] = ConnectionState.FAILED
            
            logger.error(f"Failed to connect to {connection_id}: {e}")
            return False
    
    async def disconnect(self, connection_id: str):
        """Disconnect a WebSocket connection."""
        async with self.lock:
            if connection_id in self.connections:
                try:
                    await self.connections[connection_id].close()
                except Exception as e:
                    logger.error(f"Error closing connection {connection_id}: {e}")
                
                del self.connections[connection_id]
                del self.connection_states[connection_id]
                del self.connection_stats[connection_id]
                del self.callbacks[connection_id]
                
                logger.info(f"Disconnected {connection_id}")
    
    async def send_message(self, connection_id: str, message: str):
        """Send a message through a specific connection."""
        async with self.lock:
            if connection_id not in self.connections:
                logger.warning(f"Connection {connection_id} not found")
                return False
            
            try:
                await self.connections[connection_id].send(message)
                self.connection_stats[connection_id].messages_sent += 1
                return True
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
                await self._handle_connection_error(connection_id)
                return False
    
    async def listen(self, connection_id: str):
        """Listen for messages from a specific connection."""
        async with self.lock:
            if connection_id not in self.connections:
                logger.warning(f"Connection {connection_id} not found")
                return
            
            websocket = self.connections[connection_id]
            callback = self.callbacks[connection_id]
        
        try:
            while True:
                message = await websocket.recv()
                
                # Update stats
                async with self.lock:
                    if connection_id in self.connection_stats:
                        self.connection_stats[connection_id].messages_received += 1
                        self.connection_stats[connection_id].last_message_time = time.time()
                
                # Call callback
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(message)
                    else:
                        callback(message)
                except Exception as e:
                    logger.error(f"Error in callback for {connection_id}: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning(f"Connection {connection_id} closed")
            await self._handle_connection_error(connection_id)
        except Exception as e:
            logger.error(f"Error listening to {connection_id}: {e}")
            await self._handle_connection_error(connection_id)
    
    async def _handle_connection_error(self, connection_id: str):
        """Handle connection error with reconnection logic."""
        async with self.lock:
            if connection_id in self.connection_stats:
                self.connection_stats[connection_id].reconnect_count += 1
            
            self.connection_states[connection_id] = ConnectionState.RECONNECTING
        
        # Reconnection logic
        for attempt in range(self.max_retries):
            logger.info(f"Attempting to reconnect {connection_id} (attempt {attempt + 1}/{self.max_retries})")
            await asyncio.sleep(min(2 ** attempt, 30))  # Exponential backoff
            
            # Reconnect logic would go here
            # This would need the original URL and callback
    
    async def get_connection_stats(self, connection_id: str) -> Optional[ConnectionStats]:
        """Get statistics for a specific connection."""
        async with self.lock:
            return self.connection_stats.get(connection_id)
    
    async def get_all_stats(self) -> Dict[str, ConnectionStats]:
        """Get statistics for all connections."""
        async with self.lock:
            return self.connection_stats.copy()
    
    async def check_health(self, connection_id: str) -> bool:
        """
        Check health of a connection.
        
        Returns True if connection is healthy.
        """
        async with self.lock:
            if connection_id not in self.connections:
                return False
            
            if self.connection_states[connection_id] != ConnectionState.CONNECTED:
                return False
            
            stats = self.connection_stats[connection_id]
            
            # Check if connection is stale (no messages for 60 seconds)
            if time.time() - stats.last_message_time > 60:
                logger.warning(f"Connection {connection_id} is stale")
                return False
            
            return True
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all connections."""
        results = {}
        for connection_id in self.connections.keys():
            results[connection_id] = await self.check_health(connection_id)
        return results
    
    async def close_all(self):
        """Close all connections."""
        connection_ids = list(self.connections.keys())
        for connection_id in connection_ids:
            await self.disconnect(connection_id)
        
        logger.info("All connections closed")


class ConnectionMonitor:
    """Monitor WebSocket connections and report health."""
    
    def __init__(self, connection_pool: ConnectionPool, check_interval: int = 30):
        self.connection_pool = connection_pool
        self.check_interval = check_interval
        self.running = False
        self.task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the health monitor."""
        if self.running:
            return
        
        self.running = True
        self.task = asyncio.create_task(self._monitor_loop())
        logger.info("Connection monitor started")
    
    async def stop(self):
        """Stop the health monitor."""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Connection monitor stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                health_results = await self.connection_pool.health_check_all()
                
                for connection_id, is_healthy in health_results.items():
                    if not is_healthy:
                        logger.warning(f"Connection {connection_id} is unhealthy")
                        # Trigger reconnection or alert
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(self.check_interval)
