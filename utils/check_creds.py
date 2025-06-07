from typing import Annotated

from database.common.models import db, User
from database.core import crud
from fastapi import HTTPException, Depends
from fastapi import status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from werkzeug.security import check_password_hash

security = HTTPBasic()


def get_current_username(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    is_correct_password = False

    is_correct_username = crud.check_exists()(db, User, "username",
                                              credentials.username)
    if is_correct_username:
        password_hash = crud.retrieve_single()(db, User, "username",
                                               credentials.username)[
            0].hashed_password
        is_correct_password = check_password_hash(password_hash,
                                                  credentials.password)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
