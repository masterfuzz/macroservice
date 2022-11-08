import os
import json
import sys
import rsa
import requests
import base64

from message import Message


class Session:
    def __init__(self, username: str, keyfile: str) -> None:
        with open(keyfile, "rb") as fh:
            self.privatekey = rsa.PrivateKey.load_pkcs1(fh.read())
        self.username = username

    def read_object(self, path: str):
        msg = Message("get", b"nothing", self.privatekey)
        req = requests.post(
            f"http://localhost:8080/api/{self.username}/{path}", data=msg.to_dict()
        )
        req.raise_for_status()
        return req.json()

    def write_object(self, path: str, data: str):
        enc_data = base64.encodebytes(data.encode())
        msg = Message("put", enc_data, self.privatekey)
        req = requests.post(
            f"http://localhost:8080/api/{self.username}/{path}", data=msg.to_dict()
        )
        req.raise_for_status()
        return req.json()


def main(method, path, file_name=None):
    if method.lower() == "gen":
        if os.path.exists(f"{path}_priv.pem") or os.path.exists(f"{path}_pub.pem"):
            print("Won't overwrite keys. delete them or chose a different name")
            return
        pub, priv = rsa.newkeys(512)
        with open(f"{path}_priv.pem", "wb") as fh:
            fh.write(priv.save_pkcs1())
        with open(f"{path}_pub.pem", "wb") as fh:
            fh.write(pub.save_pkcs1())
        print(f"keys created at {path}_*.pem")
        return

    # session = Session("admin", "admin_priv.pem")
    session = Session("admin", "bob_priv.pem")
    try:
        if method.lower()[0] == "g":
            obj = session.read_object(path)
            print(json.dumps(obj))
        elif method.lower()[0] == "p":
            if file_name:
                with open(file_name, "r") as fh:
                    new_data = fh.read()
            else:
                new_data = sys.stdin.read()

            resp = session.write_object(path, new_data)
            print(resp)
    except Exception as e:
        print("error")
        print(e)


if __name__ == "__main__":
    main(*sys.argv[1:])
