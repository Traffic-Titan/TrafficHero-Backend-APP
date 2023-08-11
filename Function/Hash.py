import hashlib

def encode_SHA256(text):
    return hashlib.sha256(text.encode()).hexdigest()

def decode_SHA256(text):
    return hashlib.sha256(text.encode()).hexdigest()
