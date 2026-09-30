import jwt

from Configuration.config import get_settings


settings = get_settings()


class AuthHandler:

    @staticmethod
    def decode_jwt(token: str):

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )

            return payload

        except jwt.ExpiredSignatureError:
            return None

        except jwt.InvalidTokenError:
            return None