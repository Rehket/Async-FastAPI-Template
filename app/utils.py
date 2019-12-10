import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import jwt
from jwt.exceptions import InvalidTokenError

from app.core import config

password_reset_jwt_subject = "preset"


def verify_password_reset_token(token) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
        assert decoded_token["sub"] == password_reset_jwt_subject
        return decoded_token["email"]
    except InvalidTokenError:
        return None
