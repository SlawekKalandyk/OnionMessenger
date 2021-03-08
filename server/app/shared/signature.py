from typing import Tuple
from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError
from nacl.signing import SigningKey, VerifyKey


class Signature:
    """
    ED25519 signature.

    Keys should be saved/passed between users as string, same goes for signed messages,
    but nacl classes need bytes as arguments - that's where the often used here str.encode comes in.
    Signed message has to be transformed to string with .hex() and back to hex with bytes.fromhex(...)
    """
    _encoder = HexEncoder

    @staticmethod
    def sign(private_key: str, data: str) -> str:
        if not private_key or not data:
            return None
        signing_key = SigningKey(str.encode(private_key), encoder=Signature._encoder)
        return signing_key.sign(str.encode(data), encoder=Signature._encoder).hex()

    @staticmethod
    def verify(public_key: str, signed_data: str) -> str:
        verify_key = VerifyKey(str.encode(public_key), encoder=Signature._encoder)
        try:
            message: bytes = verify_key.verify(bytes.fromhex(signed_data), encoder=Signature._encoder)
        except BadSignatureError:
            return None
        else:
            return message.decode('utf-8')

    @staticmethod
    def generate_keys() -> Tuple[str, str]:
        signing_key = SigningKey.generate()
        private_key, public_key = signing_key.encode(encoder=Signature._encoder), signing_key.verify_key.encode(encoder=Signature._encoder)
        private_key_as_str = private_key.decode('utf-8')
        public_key_as_str = public_key.decode('utf-8')
        return private_key_as_str, public_key_as_str
