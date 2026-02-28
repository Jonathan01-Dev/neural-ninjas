from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

from node_id import get_node_id_hex, get_node_id_bytes, PUB_KEY_PATH


def _write_pub_key(path: Path) -> None:
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(pub_bytes)


if __name__ == "__main__":
    # Save original key (if any)
    original = PUB_KEY_PATH.read_bytes() if PUB_KEY_PATH.exists() else None

    try:
        # Generate first key and ID
        _write_pub_key(PUB_KEY_PATH)
        id1_hex = get_node_id_hex()
        id1_bytes = get_node_id_bytes()

        # Generate second key and ID
        _write_pub_key(PUB_KEY_PATH)
        id2_hex = get_node_id_hex()
        id2_bytes = get_node_id_bytes()

        assert id1_hex != id2_hex, "IDs should differ for different keys"
        assert id1_bytes != id2_bytes, "IDs should differ for different keys"
        assert len(id1_bytes) == 32, "SHA-256 digest should be 32 bytes"
        print("OK: node_id is unique and correctly sized.")
    finally:
        # Restore original key
        if original is not None:
            PUB_KEY_PATH.write_bytes(original)
