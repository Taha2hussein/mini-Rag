from fastapi import Header, Depends, status, HTTPException
from typing import Annotated, Union
from sqlalchemy.orm import Session
from src.Security.authHandler import HashHelper
from src.services.userService import UserService
from src.DataBase import get_db
from src.schema.UserSchema import UserOutput
from src.Security.hashHelper import Auth_Handler
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_db),
) -> UserOutput:

    token = credentials.credentials

    payload = Auth_Handler.decode_JWT(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authentication Credential",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authentication Credential",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = UserService(session=session).get_user_ById(user_id)

    return UserOutput(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
    )