# utils/security.py
import bcrypt

def hash_password(password: str) -> str:
    """
    Hashes a plaintext password using bcrypt.
    """
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(hashed_password: str, password: str) -> bool:
    """
    Verifies a plaintext password against the hashed version.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
