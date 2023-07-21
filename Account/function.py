import random

def generate_verification_code():
    return str(random.randint(100000, 999999))