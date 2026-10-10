import csv
import hashlib
import hmac
import os
import secrets

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
USERS_PATH = PROJECT_ROOT / "data" / "users.csv"

USER_COLUMNS = [
    "email",
    "full_name",
    "salt",
    "password_hash",
]


def hash_password(password, salt=None):
    """Hash a password using PBKDF2-HMAC-SHA256."""
    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        600_000,
    ).hex()

    return salt, password_hash


def load_users():
    """Load registered accounts from the users CSV."""
    if not USERS_PATH.exists():
        return []

    with USERS_PATH.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        return list(csv.DictReader(file))

def account_exists():
    """Return True if a bakery account has already been registered."""
    return len(load_users()) > 0


def register_user(full_name, email, password):
    """Register a new account if the email is not already used."""
    full_name = full_name.strip()
    email = email.strip().lower()

    if not full_name:
        raise ValueError("Please enter your full name.")

    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("Please enter a valid email address.")

    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")

    users = load_users()

    if users:
        raise ValueError(
            "An account has already been registered. "
            "Please sign in instead."
        )

    if any(user["email"].lower() == email for user in users):
        raise ValueError("An account with this email already exists.")

    salt, password_hash = hash_password(password)

    USERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_exists = USERS_PATH.exists()

    with USERS_PATH.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=USER_COLUMNS)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "email": email,
            "full_name": full_name,
            "salt": salt,
            "password_hash": password_hash,
        })


def authenticate_user(email, password):
    """Return the user record if the credentials are valid."""
    email = email.strip().lower()

    for user in load_users():
        if user["email"].lower() != email:
            continue

        _, supplied_hash = hash_password(
            password,
            salt=user["salt"],
        )

        if hmac.compare_digest(
            supplied_hash,
            user["password_hash"],
        ):
            return {
                "email": user["email"],
                "full_name": user["full_name"],
            }

    return None