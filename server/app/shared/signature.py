from typing import Tuple
from app.shared.config import AuthenticationConfiguration
from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError
from nacl.signing import SigningKey
from nacl.signing import VerifyKey

from app.shared.helpful_abstractions import Singleton

"""
Keys should be saved/passed between users as string, same goes for signed messages,
but nacl classes need bytes as arguments - that's where the often used here str.encode comes in.
Signed message has to be transformed to string with .hex() and back to hex with bytes.fromhex(...)
"""
class Signature(metaclass=Singleton):
    def __init__(self):
        self._encoder = HexEncoder
        self._private_key: str = AuthenticationConfiguration.get_signature_private_key()
        self._public_key: str = AuthenticationConfiguration.get_signature_public_key()
        if not self._private_key and not self._public_key:
            self._private_key, self._public_key = self._generate_keys()
        self._signing_key = SigningKey(str.encode(self._private_key), encoder=self._encoder)

    def sign(self, data: str) -> str:   
        return self._signing_key.sign(str.encode(data), encoder=self._encoder).hex()

    def verify(self, other_public_key: str, signed_data: str) -> str:
        verify_key = VerifyKey(str.encode(other_public_key), encoder=self._encoder)
        try:
            message: bytes = verify_key.verify(bytes.fromhex(signed_data), encoder=self._encoder)
        except BadSignatureError:
            return None
        else:
            return message.decode('utf-8')

    def get_private_key(self) -> str:
        return self._private_key

    def get_public_key(self) -> str:
        return self._public_key

    def _generate_keys(self) -> Tuple[str, str]:
        signing_key = SigningKey.generate()
        private_key, public_key = signing_key.encode(encoder=self._encoder), signing_key.verify_key.encode(encoder=self._encoder)
        private_key_as_str = private_key.decode('utf-8')
        public_key_as_str = public_key.decode('utf-8')
        AuthenticationConfiguration.save_signature_private_key(private_key_as_str)
        AuthenticationConfiguration.save_signature_public_key(public_key_as_str)
        return private_key_as_str, public_key_as_str

    
