import base64
import rsa


# A message in flight:
# method: 'GET' or 'PUT'
# data: base64 encoded (anything)
# signature: base64 encoded (signature of method + data (base64 encoded))
# at rest:
# method: still just a string
# data: bytes
# signature: bytes


class Message:
    def __init__(
        self, method: str = None, data: bytes = None, private_key: rsa.PrivateKey = None
    ) -> None:
        self.method: str = method
        self.data: bytes = data
        if private_key:
            self.sign(private_key)
        else:
            self.signature: bytes = None

    @classmethod
    def from_forms(cls, forms):
        new = cls()
        new.signature = base64.decodebytes(forms["signature"].encode())
        new.method = forms["method"]
        new.data = base64.decodebytes(forms["data"].encode())
        return new

    @property
    def to_sign(self):
        return self.method.encode() + base64.encodebytes(self.data)

    def verify(self, pub_key):
        return rsa.verify(self.to_sign, self.signature, pub_key)

    def sign(self, priv_key):
        self.signature = rsa.sign(self.to_sign, priv_key, "MD5")

    def to_dict(self):
        return {
            "method": self.method.lower(),
            "data": base64.encodebytes(self.data).decode(),
            "signature": base64.encodebytes(self.signature).decode(),
        }
