from typing import Annotated

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from shared_utils import messages
from shared_utils.core.conf import settings
from shared_utils.schemas.user import User


security = HTTPBearer()


async def get_current_user(token: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> User:
    """
    Retrieves the current authenticated user by verifying the provided token.

    This asynchronous function sends a request to an external authentication service
    to validate the user's token and fetch user details. If the token is invalid or
    the request fails, an HTTPException is raised with a 401 Unauthorized status code.

    Args:
        - token (HTTPAuthorizationCredentials): The HTTP authorization token, which contains the scheme (e.g., "Bearer")
          and the token credentials (the actual token).

    Returns:
        - User: A User object populated with the response data from the authentication service.

    Raises:
        - HTTPException: If the token is invalid or the authentication service returns a non-200 status code,
          a 401 Unauthorized exception is raised.
    """

    async with httpx.AsyncClient(timeout=settings.USER_REQUEST_TIMEOUT) as client:
        response = await client.get(
            url=settings.USER_AUTH_URL,
            headers={'Authorization': f'{token.scheme} {token.credentials}'}
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=messages.INVALID_TOKEN_MESSAGE
            )

        return User(
            ** response.json()
        )


async def get_current_admin_user(current_user = Depends(get_current_user)) -> User:
    """
    Retrieves the current authenticated user and checks if they are an admin.

    This asynchronous function first uses the `get_current_user` dependency to obtain
    the current authenticated user. It then checks if the user has admin privileges.
    If the user is not an admin, an HTTPException with a 403 Forbidden status is raised.

    Args:
        - current_user (User): The current authenticated user, automatically injected  by the
          `get_current_user` dependency.

    Returns:
        - User: The `User` object representing the authenticated user, but only if they have admin privileges.

    Raises:
        - HTTPException: If the user does not have admin privileges, a 403 Forbidden exception is raised with
          a relevant error message.
    """

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_FORBIDDEN_MESSAGE
        )

    return current_user


async def get_user_by_id(user_id: int, token: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> User:
    """
    Retrieves user information by user ID from an external service.

    This asynchronous function sends a request to an external service to fetch user data
    for a given `user_id`, using the provided authorization token to authenticate the request.
    If the user is not found, it raises an HTTPException with a 404 Not Found status.

    Args:
        - user_id (int): The unique identifier of the user whose information is to be retrieved.
        - token (HTTPAuthorizationCredentials): The HTTP authorization token, which contains the authentication scheme
          (e.g., "Bearer") and the token credentials (actual token).

    Returns:
        - User: A User object populated with the response data from the external service.

    Raises:
        - HTTPException: If the user is not found or the request to the external service fails,
         a 404 Not Found exception is raised.
    """
    async with httpx.AsyncClient(timeout=settings.USER_REQUEST_TIMEOUT) as client:
        response = await client.get(
            url=settings.USER_INFO_URL.format(user_id=str(user_id)),
            headers={'Authorization': f'{token.scheme} {token.credentials}'}
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=messages.USER_NOT_FOUND_MESSAGE
            )

        return User(
            ** response.json()
        )
