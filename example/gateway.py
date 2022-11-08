import os
import base64
import rsa
from bottle import route, run, request, HTTPError, post
from message import Message


def load_key(path: str) -> rsa.PublicKey:
    with open(path, "rb") as fh:
        return rsa.PublicKey.load_pkcs1(fh.read())


admin_key = load_key("admin_pub.pem")


def find_user(name: str) -> rsa.PublicKey:
    if name == "admin":
        return admin_key
    return load_key(f"data/admin/user_key_{name}.pem")


def read_data(user: str, path: str):
    with open(os.path.join("data", user, path), "rb") as fh:
        return fh.read()


def write_data(user: str, path: str, data: bytes):
    os.makedirs(f"data/{user}", exist_ok=True)
    with open(os.path.join("data", user, path), "wb") as fh:
        return fh.write(data)


@post("/api/<username>/<resourcepath>")
def api(username, resourcepath):
    msg = Message.from_forms(request.forms)

    try:
        key = find_user(username)
        msg.verify(key)
    except Exception as e:
        print(e)
        raise HTTPError(403)

    if msg.method.lower() == "get":
        try:
            data = read_data(username, resourcepath)
            return {resourcepath: base64.encodebytes(data).decode()}
        except Exception as e:
            print(e)
            raise HTTPError(404)

    if msg.method.lower() == "put":
        try:
            count = write_data(username, resourcepath, base64.decodebytes(msg.data))
            return {"put": count}
        except Exception as e:
            print(e)
            raise e

    raise HTTPError(405)


@route("/")
def ui():
    return "hello"


if __name__ == "__main__":
    run(port=8080)
