from __future__ import annotations

from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes


@dataclass
class EphemeralKeyPair:
    private_key: x25519.X25519PrivateKey
    public_key: x25519.X25519PublicKey


def generate_ephemeral_keypair() -> EphemeralKeyPair:
    """
    Génère une paire de clés X25519 éphémères.
    Utilisée pour le handshake (Forward Secrecy).
    """
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()
    return EphemeralKeyPair(private_key=private_key, public_key=public_key)


def derive_shared_secret(
    my_private: x25519.X25519PrivateKey,
    peer_public: x25519.X25519PublicKey,
) -> bytes:
    """
    Calcule le secret partagé X25519.
    """
    return my_private.exchange(peer_public)


def derive_session_key(shared_secret: bytes, salt: bytes | None = None) -> bytes:
    """
    Dérive une clé de session (32 bytes) à partir du secret partagé.
    """
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=b"archipel-v1",
    )
    return hkdf.derive(shared_secret)


if __name__ == "__main__":
    # Test rapide local (pas un vrai handshake réseau)
    alice = generate_ephemeral_keypair()
    bob = generate_ephemeral_keypair()

    s1 = derive_shared_secret(alice.private_key, bob.public_key)
    s2 = derive_shared_secret(bob.private_key, alice.public_key)

    assert s1 == s2, "Shared secrets should match"
    key = derive_session_key(s1)
    print("OK: session key length =", len(key))
