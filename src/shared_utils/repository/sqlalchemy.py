from typing import Sequence, Optional, Any

from sqlalchemy.sql import select
from sqlalchemy.ext.asyncio import AsyncSession
from shared_utils.db.base import Base
from shared_utils.exceptions import ObjDoesNotExist
from shared_utils.repository.base import AbstractBaseRepository


class SQLAlchemyModelRepository[T: Base](AbstractBaseRepository[T]):
    """
    A generic asynchronous repository for SQLAlchemy models.

    This class provides an implementation of the AbstractBaseRepository interface
    for managing SQLAlchemy ORM models using an asynchronous session.
    """

    def __init__(self, db: AsyncSession, model_class: T):
        """
        Initializes the repository with a database session and model class.

        Args:
            - db (AsyncSession): The SQLAlchemy asynchronous session.
            - model_class (T): The model class to be managed by the repository.
        """
        self.db = db
        self.model_class = model_class

    async def create(self, **kwargs) -> T:
        """
        Creates a new instance of the model with the given attributes.

        Args:
            - **kwargs: Fields to populate the new model instance.

        Returns:
            - T: The newly created and persisted model instance.
        """
        instance = self.model_class(**kwargs)
        self.db.add(instance)

        await self.db.commit()
        await self.db.refresh(instance)

        return instance

    async def get_all(self) -> Sequence[T]:
        """
        Retrieves all instances of the model from the database.

        Returns:
            - Sequence[T]: A list of all model instances.
        """
        result = await self.db.execute(
            select(self.model_class)
        )
        return result.scalars().all()

    async def get_by_id(self, id: Any) -> T:
        """
        Retrieves a single model instance by its unique identifier.

        Args:
            - id (Any): The unique identifier of the model instance.

        Returns:
            - T: The model instance if found.

        Raises:
            - ObjDoesNotExist: If no instance is found with the given ID.
        """
        result = await self.db.execute(
            select(self.model_class).filter_by(id=id)
        )

        result = result.scalar_one_or_none()
        if not result:
            raise ObjDoesNotExist

        return result

    async def filter_by(self, **kwargs) -> Optional[Sequence[T]]:
        """
        Retrieves model instances that match the given filtering criteria.

        Args:
            - **kwargs: Filtering conditions as keyword arguments.

        Returns:
            - Optional[Sequence[T]]: A list of matching model instances, or None if no match is found.
        """
        result = await self.db.execute(
            select(self.model_class).filter_by(**kwargs)
        )
        return result.scalar_one_or_none()

    async def update(self, id: Any, **kwargs) -> T:
        """
        Updates an existing model instance with new field values.

        Args:
            - id (Any): The unique identifier of the model instance to update.
            - **kwargs: Field-value pairs to update.

        Returns:
            - T: The updated model instance.

        Raises:
            - ObjDoesNotExist: If no instance is found with the given ID.
        """
        obj = await self.get_by_id(id=id)

        for field_name, new_field_value in kwargs.items():
            if new_field_value and \
               hasattr(obj, field_name) and \
               getattr(obj, field_name) != new_field_value:
                setattr(obj, field_name, new_field_value)

        await self.db.commit()
        await self.db.refresh(obj)

        return obj

    async def delete(self, id: Any) -> None:
        """
        Deletes the model instance with the specified ID from the database.

        Args:
            - id (Any): The unique identifier of the model instance to delete.

        Raises:
            - ObjDoesNotExist: If no instance is found with the given ID.
        """
        obj = await self.get_by_id(id=id)
        await self.db.delete(obj)
        await self.db.commit()
