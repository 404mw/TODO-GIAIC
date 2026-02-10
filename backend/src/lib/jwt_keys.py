"""JWT RSA key pair generation and management.

Provides utilities to generate and manage RSA key pairs for JWT signing.
Keys can be generated during build or loaded from environment variables.
"""

import os
from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_rsa_key_pair() -> tuple[str, str]:
    """Generate a new RSA key pair for JWT signing.

    Returns:
        tuple[str, str]: (private_key_pem, public_key_pem)
    """
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Serialize private key to PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    # Get public key and serialize to PEM format
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    return private_pem, public_pem


def save_keys_to_file(private_key: str, public_key: str, directory: str = ".") -> tuple[str, str]:
    """Save RSA keys to files.

    Args:
        private_key: Private key in PEM format
        public_key: Public key in PEM format
        directory: Directory to save keys (default: current directory)

    Returns:
        tuple[str, str]: (private_key_path, public_key_path)
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)

    private_path = dir_path / "jwt_private_key.pem"
    public_path = dir_path / "jwt_public_key.pem"

    # Write keys with secure permissions
    private_path.write_text(private_key)
    private_path.chmod(0o600)  # Read/write for owner only

    public_path.write_text(public_key)
    public_path.chmod(0o644)  # Read for all, write for owner

    return str(private_path), str(public_path)


def get_or_generate_keys() -> tuple[str, str]:
    """Get existing keys or generate new ones.

    Priority:
    1. Environment variables (JWT_PRIVATE_KEY, JWT_PUBLIC_KEY)
    2. Key files (./keys/jwt_private_key.pem, ./keys/jwt_public_key.pem)
    3. Generate new keys and save to ./keys/

    Returns:
        tuple[str, str]: (private_key_pem, public_key_pem)
    """
    # Check environment variables first
    env_private = os.getenv("JWT_PRIVATE_KEY")
    env_public = os.getenv("JWT_PUBLIC_KEY")

    if env_private and env_public:
        return env_private, env_public

    # Check for existing key files
    keys_dir = Path("keys")
    private_path = keys_dir / "jwt_private_key.pem"
    public_path = keys_dir / "jwt_public_key.pem"

    if private_path.exists() and public_path.exists():
        return private_path.read_text(), public_path.read_text()

    # Generate new keys
    private_key, public_key = generate_rsa_key_pair()

    # Save to files for reuse
    save_keys_to_file(private_key, public_key, directory="keys")

    return private_key, public_key


if __name__ == "__main__":
    """Generate keys when run as a script."""
    private_key, public_key = generate_rsa_key_pair()
    private_path, public_path = save_keys_to_file(private_key, public_key, directory="keys")

    print("SUCCESS: JWT RSA key pair generated successfully!")
    print(f"Private key: {private_path}")
    print(f"Public key: {public_path}")
    print("\nWARNING: Add these to your .env file or set as environment variables:")
    print(f"\nJWT_PRIVATE_KEY_PATH={private_path}")
    print(f"JWT_PUBLIC_KEY_PATH={public_path}")
    print("\nSECURITY: Keep the private key secure and never commit it to version control!")
