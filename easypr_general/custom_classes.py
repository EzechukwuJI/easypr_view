from cryptography.fernet import Fernet
import base64


class Hasher():
    def __init__(self):
        self.key   =   Fernet.generate_key()
        self.cipher_suite   =   Fernet(self.key)

    def encrypt(self, raw_string):
    	byte_string = raw_string.encode('utf-8')
        return self.cipher_suite.encrypt(byte_string)

    def decrypt(self, cipher_text):
        return self.cipher_suite.decrypt(base64.b64encode(cipher_text))