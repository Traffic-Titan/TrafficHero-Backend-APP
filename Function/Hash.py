import hashlib

def encodeSHA256(text):
    return hashlib.sha256(text.encode()).hexdigest()

def decodeSHA256(text):
    return hashlib.sha256(text.encode()).hexdigest()
