import os
import base64
import rsa
from bottle import get, run, request, HTTPError, post, static_file
from message import Message


class Gateway:
    def __init__(self, admin_key_path=None, data_path=None) -> None:
        self.admin_key = self.load_key(admin_key_path or "admin_pub.pem")
        print(f"loaded admin key {self.admin_key}")
        self.data_path = data_path or "data"
        print(f"useing data path {self.data_path}")

    @staticmethod
    def load_key(path: str) -> rsa.PublicKey:
        with open(path, "rb") as fh:
            return rsa.PublicKey.load_pkcs1(fh.read())

    def user_key(self, name: str) -> rsa.PublicKey:
        if name == "admin":
            return self.admin_key
        return self.load_key(
            os.path.join(self.data_path, "admin", f"user_key_{name}.pem")
        )

    def read_data(self, user: str, path: str):
        with open(os.path.join(self.data_path, user, path), "rb") as fh:
            return fh.read()

    def write_data(self, user: str, path: str, data: bytes):
        os.makedirs(os.path.join(self.data_path, user), exist_ok=True)
        with open(os.path.join("data", user, path), "wb") as fh:
            return fh.write(data)


gateway = Gateway(
    admin_key_path=os.environ.get("ADMIN_KEY_PATH"),
    data_path=os.environ.get("DATA_PATH"),
)


@post("/api/<username>/<resourcepath>")
def api(username, resourcepath):
    msg = Message.from_forms(request.forms)

    try:
        key = gateway.user_key(username)
        msg.verify(key)
    except Exception as e:
        print(e)
        raise HTTPError(403)

    if msg.method.lower() == "get":
        try:
            data = gateway.read_data(username, resourcepath)
            return {resourcepath: base64.encodebytes(data).decode()}
        except Exception as e:
            print(e)
            raise HTTPError(404)

    if msg.method.lower() == "put":
        try:
            count = gateway.write_data(
                username, resourcepath, base64.decodebytes(msg.data)
            )
            return {"put": count}
        except Exception as e:
            print(e)
            raise e

    raise HTTPError(405)


@get("/<filepath:re:.*\.(html|js|wasm)>")
def ui(filepath):
    return static_file(filepath, root="data/admin/static")


if __name__ == "__main__":
    run(host="0.0.0.0", port=8080)
