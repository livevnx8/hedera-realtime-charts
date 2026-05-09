"""TCP socket optimization for low-latency networking."""

import socket
from typing import Optional


class OptimizedSocket:
    """Create optimized TCP sockets for low-latency communication."""

    @staticmethod
    def create_socket() -> socket.socket:
        """
        Create an optimized TCP socket.

        Returns:
            Configured socket object
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Disable Nagle's algorithm for immediate sending
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        
        # Enable quick ACK for faster acknowledgments
        try:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)
        except AttributeError:
            # TCP_QUICKACK not available on all platforms
            pass
        
        # Set socket to non-blocking mode
        sock.setblocking(False)
        
        # Enable keep-alive
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        
        # Set keep-alive parameters (Linux)
        try:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 10)  # 10 seconds
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5)   # 5 seconds
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)     # 3 retries
        except AttributeError:
            pass
        
        return sock

    @staticmethod
    def optimize_existing_socket(sock: socket.socket):
        """
        Optimize an existing socket.

        Args:
            sock: Existing socket to optimize
        """
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        
        try:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)
        except AttributeError:
            pass
        
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)


# Example usage
if __name__ == "__main__":
    sock = OptimizedSocket.create_socket()
    print("Optimized socket created successfully")
    sock.close()
