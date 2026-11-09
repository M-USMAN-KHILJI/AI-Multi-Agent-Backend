import hashlib
import hmac
import os

def hash_password(password: str) -> str:
    """
    Hash a password securely using PBKDF2 with SHA-256 and a random salt.
    Format: salt$hash
    """
    salt = os.urandom(16).hex()
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    return f"{salt}${hashed}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against the stored salt$hash string.
    """
    try:
        salt, expected_hash = hashed_password.split('$', 1)
        actual_hash = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return hmac.compare_digest(actual_hash, expected_hash)
    except Exception:
        return False

