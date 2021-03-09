from app.shared.signature import Signature
import base64
import uuid
import hashlib
from hashlib import sha3_256


def generate_random_guid() -> str:
    return str(uuid.uuid4())


def get_onion_address_from_public_key(public_key: str) -> str:
    constant = b".onion checksum"
    pub = Signature.encode_key_to_bytes(public_key)
    version = b'\x03'
    checksum = sha3_256(constant + pub + version).digest()[:2]
    address = base64.b32encode(pub + checksum + version).decode().lower()
    return f"{address}.onion"


def stem_compatible_base64_blob_from_private_key(private_key: str) -> str:
    b = 256

    def bit(h: bytes, i: int) -> int:
        return (h[i // 8] >> (i % 8)) & 1

    def encode_int(y: int) -> bytes:
        bits = [(y >> i) & 1 for i in range(b)]
        return b''.join([bytes([(sum([bits[i * 8 + j] << j for j in range(8)]))]) for i in range(b // 8)])

    def expand_private_key(sk: bytes) -> bytes:
        h = hashlib.sha512(sk).digest()
        a = 2 ** (b - 2) + sum(2 ** i * bit(h, i) for i in range(3, b - 2))
        k = b''.join([bytes([h[i]]) for i in range(b // 8, b // 4)])
        assert len(k) == 32
        return encode_int(a) + k

    private_key_as_bytes = Signature.encode_key_to_bytes(private_key)
    expanded_private_key = expand_private_key(private_key_as_bytes)
    return base64.b64encode(expanded_private_key).decode()