"""Offline packaging probe: load and exercise the actual native dependencies."""


def check_runtime():
    # Load Python's TLS before cryptography, as discovery/pairing can do at runtime.
    import ssl
    ssl.create_default_context()
    import paramiko
    import bcrypt
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from nacl.signing import SigningKey

    message = b'cytv offline packaging check'
    key = paramiko.RSAKey.generate(2048)
    signature = key.sign_ssh_data(message, algorithm='rsa-sha2-256')
    if not key.verify_ssh_sig(message, paramiko.Message(signature.asbytes())):
        raise RuntimeError('SSH signature verification failed')
    cipher = AESGCM(AESGCM.generate_key(bit_length=128))
    nonce = b'\0' * 12
    if cipher.decrypt(nonce, cipher.encrypt(nonce, message, None), None) != message:
        raise RuntimeError('SSH crypto verification failed')
    signing_key = SigningKey.generate()
    if signing_key.verify_key.verify(signing_key.sign(message)) != message:
        raise RuntimeError('SSH Ed25519 verification failed')
    bcrypt.kdf(password=message, salt=b'cytv offline salt', desired_key_bytes=32,
               rounds=4, ignore_few_rounds=True)
