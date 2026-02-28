from pathlib import Path
import hashlib

KEY_DIR = Path("keys")
PUB_KEY_PATH = KEY_DIR / "node_ed25519_public.pem"


def get_node_id_bytes() -> bytes:
    """
    Identifiant stable du nœud (bytes).
    Utilisé pour les paquets réseau.
    """
    data = PUB_KEY_PATH.read_bytes()
    return hashlib.sha256(data).digest()


def get_node_id_hex() -> str:
    """
    Identifiant stable du nœud (hex).
    Utile pour logs/CLI/debug.
    """
    return get_node_id_bytes().hex()


if __name__ == "__main__":
    print(get_node_id_hex())
