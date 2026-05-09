"""Binary serialization using MessagePack for low-latency data transfer."""

import msgpack
from typing import Dict, Any


class MessagePackSerializer:
    """Serialize/deserialize data using MessagePack for minimal overhead."""

    @staticmethod
    def serialize(data: Dict[str, Any]) -> bytes:
        """
        Serialize data to MessagePack format.

        Args:
            data: Dictionary to serialize

        Returns:
            MessagePack encoded bytes
        """
        return msgpack.packb(data, use_bin_type=True)

    @staticmethod
    def deserialize(data: bytes) -> Dict[str, Any]:
        """
        Deserialize MessagePack data to dictionary.

        Args:
            data: MessagePack encoded bytes

        Returns:
            Deserialized dictionary
        """
        return msgpack.unpackb(data, raw=False)


# Example usage
if __name__ == "__main__":
    serializer = MessagePackSerializer()
    
    # Test data
    test_data = {
        "symbol": "BTCUSDT",
        "price": 50000.0,
        "quantity": 0.5,
        "time": 1234567890,
        "latency": 10.5,
    }
    
    # Serialize
    serialized = serializer.serialize(test_data)
    print(f"Serialized size: {len(serialized)} bytes")
    
    # Deserialize
    deserialized = serializer.deserialize(serialized)
    print(f"Deserialized: {deserialized}")
