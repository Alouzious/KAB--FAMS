import re
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@" + re.escape(settings.ALLOWED_EMAIL_DOMAIN) + r"$")


def is_valid_university_email(email: str) -> bool:
    """Only allow emails ending in @kab.ac.ug"""
    return bool(EMAIL_REGEX.match(email.lower()))


def extract_admission_year(email: str) -> int | None:
    """
    Best-effort extraction of a 4-digit year prefix from the email,
    e.g. '2024akcs5193gf@kab.ac.ug' -> 2024.
    Returns None if no confident match is found — caller must let
    the student confirm/enter it manually in that case.
    """
    match = re.match(r"^(20\d{2})", email)
    if match:
        return int(match.group(1))
    return None


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])