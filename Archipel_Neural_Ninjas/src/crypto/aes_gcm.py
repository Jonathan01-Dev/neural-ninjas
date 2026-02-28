from __future__ import annotations

import os
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


@dataclass
class EncryptedMessage:
    nonce: bytes  # 12 bytes
    ciphertext: bytes  # includes auth tag at end


def encrypt_aes_gcm(key: bytes, plaintext: bytes, aad: bytes | None = None) -> EncryptedMessage:
    """
    Chiffre un message avec AES-256-GCM.
    key: 32 bytes
    aad: données authentifiées optionnelles (ex: header)
    """
    if len(key) != 32:
        raise ValueError("AES-256-GCM key must be 32 bytes")
    nonce = os.urandom(12)  # 96-bit nonce
    aes = AESGCM(key)
    ct = aes.encrypt(nonce, plaintext, aad)
    return EncryptedMessage(nonce=nonce, ciphertext=ct)


def decrypt_aes_gcm(key: bytes, msg: EncryptedMessage, aad: bytes | None = None) -> bytes:
    """
    Déchiffre un message AES-256-GCM.
    """
    if len(key) != 32:
        raise ValueError("AES-256-GCM key must be 32 bytes")
    aes = AESGCM(key)
    return aes.decrypt(msg.nonce, msg.ciphertext, aad)


if __name__ == "__main__":
    # Test rapide
    key = os.urandom(32)
    plaintext = b"hello archipel"
    msg = encrypt_aes_gcm(key, plaintext)
    out = decrypt_aes_gcm(key, msg)
    assert out == plaintext
    print("OK: AES-GCM encrypt/decrypt")
