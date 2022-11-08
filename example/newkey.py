import rsa

pub, priv = rsa.newkeys(512)

with open("pub.pem", "wb") as fh:
    fh.write(pub.save_pkcs1())

with open("priv.pem", "wb") as fh:
    fh.write(priv.save_pkcs1())
