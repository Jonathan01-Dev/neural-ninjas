from session_keys import generate_ephemeral_keypair, derive_shared_secret, derive_session_key
from aes_gcm import encrypt_aes_gcm, decrypt_aes_gcm


def main() -> None:
    # 1) Alice et Bob génèrent des clés éphémères
    alice = generate_ephemeral_keypair()
    bob = generate_ephemeral_keypair()

    # 2) Échange des clés publiques éphémères
    alice_pub = alice.public_key
    bob_pub = bob.public_key

    # 3) Calcul du secret partagé
    shared_a = derive_shared_secret(alice.private_key, bob_pub)
    shared_b = derive_shared_secret(bob.private_key, alice_pub)

    # 4) Dérivation de la clé de session (identique des deux côtés)
    key_a = derive_session_key(shared_a)
    key_b = derive_session_key(shared_b)

    assert key_a == key_b, "Les clés de session doivent être identiques"

    # 5) Chiffrement et déchiffrement d’un message test
    plaintext = b"Hello Bob, this is Alice."
    encrypted = encrypt_aes_gcm(key_a, plaintext)
    decrypted = decrypt_aes_gcm(key_b, encrypted)

    print("Message clair :", plaintext.decode())
    print("Message recu :", decrypted.decode())
    print("OK: handshake + AES-GCM fonctionnels")


if __name__ == "__main__":
    main()
