from typing import  Optional
from pydantic_settings import BaseSettings
from shared_utils.utils import validate_pydantic_model_field


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: Optional[str] = None
    USER_AUTH_URL: Optional[str] = None
    USER_INFO_URL: Optional[str] = None
    USER_REQUEST_TIMEOUT: Optional[int] = 10


def update_settings(**new_settings) -> None:
    """
    Update the settings with new values.
    This function takes keyword arguments representing the field names and their new values.

    Args:
        - new_settings: A dictionary of field names and their new values.

    Raises:
        - KeyError: If a field name does not exist in the settings.
        - ValueError: If the new value does not pass validation for the field.
    """

    for field_name, value in new_settings.items():
        if hasattr(settings, field_name):
            validate_pydantic_model_field(
                model=Settings,
                field_name=field_name,
                value=value
            )
            setattr(settings, field_name, value)
        else:
            raise KeyError(
                f"Field '{field_name}' does not exist in settings."
            )


settings = Settings()
