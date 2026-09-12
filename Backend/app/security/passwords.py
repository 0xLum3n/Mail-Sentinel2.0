"""Password hashing helpers."""

from passlib.context import CryptContext

# bcrypt_sha256 hashes the password with SHA-256 before passing it to bcrypt,
# avoiding bcrypt's 72-byte password truncation while retaining bcrypt's cost model.
_pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password."""
    return _pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against its stored hash."""
    return _pwd_context.verify(password, password_hash)
