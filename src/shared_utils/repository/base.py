from abc import ABC, abstractmethod
from typing import Sequence, Optional, Any


class AbstractBaseRepository[T](ABC):
    """
    Abstract base class for a generic repository.

    This class defines a standard interface for basic CRUD (Create, Read, Update, Delete)
    operations and filtering, to be implemented by concrete repository classes for specific data sources.
    """

    @abstractmethod
    def create(self, **kwargs) -> T:
        """
         Creates a new entity instance using the provided keyword arguments.
        """
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> Sequence[T]:
        """
        Retrieves all entities from the data source.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id: Any) -> Optional[T]:
        """
        Retrieves a single entity by its unique identifier.
        """
        raise NotImplementedError

    @abstractmethod
    def filter_by(self, **kwargs) -> Sequence[T]:
        """
        Returns a list of entities that match the given filtering criteria.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, id: Any, **kwargs) -> T:
        """
        Updates an existing entity identified by the given ID with new values.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, id: Any) -> None:
        """
        Deletes the entity with the specified ID from the data source.
        """
        raise NotImplementedError
