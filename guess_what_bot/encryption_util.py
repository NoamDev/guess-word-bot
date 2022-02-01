import os
import base64
import codecs

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

key = base64.b64decode(os.environ['AES_KEY'].encode('utf8'))

def encrypt(word, lang):
    try:
        data = word.encode('utf8')+lang.encode('utf8')
        if len(data)%16 != 0:
            data+=b"\x00"*(16-len(data)%16)
        print(len(data))
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        cipher_text= encryptor.update(data) + encryptor.finalize()
        return base64.b64encode(iv+cipher_text,altchars=b'-_')
    except:
        raise ValueError(f"Could not encrypt data {data}")

def decrypt(data):
    try:
        data=base64.b64decode(data,altchars=b'-_')
        iv=data[:16]
        ct=data[16:]
        print(iv)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        message = codecs.decode(decryptor.update(ct)+decryptor.finalize(), 'utf8').replace('\0','')
        word = message[:-2]
        lang = message[-2:]
        return word, lang
    except:
        raise ValueError(f"Could not decrypt data {data}")