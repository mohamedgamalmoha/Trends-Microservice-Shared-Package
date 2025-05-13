from typing import Generic, Sequence, Any, get_args

from sqlalchemy.sql import Select, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from shared_utils.db.base import Base
from shared_utils.exceptions import ObjDoesNotExist
from shared_utils.repository.base import AbstractBaseRepository
from shared_utils.pagination import Paginator


class SQLAlchemyModelRepository[T: Base](AbstractBaseRepository[T]):
    """
    A generic asynchronous repository for SQLAlchemy models.

    This class provides an implementation of the AbstractBaseRepository interface
    for managing SQLAlchemy ORM models using an asynchronous session.
    """

    def __init__(self, db: AsyncSession):
        """
        Initializes the repository with a database session.

        Args:
            - db (AsyncSession): The SQLAlchemy asynchronous session.
        """
        self.db = db

    @property
    def model_class(self):
        """
        Retrieves the model class associated with the repository.

        This property returns the model class type that the repository is managing.
        It uses the repository's generic type parameter `T` to determine the model class,
        which is typically passed when the repository is initialized.

        Returns:
            - Type[T]: The model class associated with this repository.
        """
        orig_base = self.__class__.__orig_bases__[0]
        return get_args(orig_base)[0]

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

        if instance is not None:
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

    async def filter_by(self, **kwargs) -> Sequence[T]:
        """
        Retrieves model instances that match the given filtering criteria.

        Args:
            - **kwargs: Filtering conditions as keyword arguments.

        Returns:
            - Sequence[T]: A list of matching model instances.
        """
        result = await self.db.execute(
            select(self.model_class).filter_by(**kwargs)
        )
        return result.all()

    async def get_by(self, **kwargs) -> T:
        """
        Retrieves a single model instance that matches the given filtering criteria.

        Args:
            - **kwargs: Filtering conditions as keyword arguments.

        Returns:
            - T: The model instance if found.

        Raises:
            - ObjDoesNotExist: If no instance is found with the given criteria.
        """
        result = await self.db.execute(
            select(self.model_class).filter_by(**kwargs)
        )

        result = result.scalar_one_or_none()
        if not result:
            raise ObjDoesNotExist

        return result

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
        result = await self.get_by(id=id)

    def get_filter_query(self, **filters) -> Select:
        """
        Create a filter query for the model.

        Args:
            - **filters: Filters to apply to the query.

        Returns:
            - Select: A SQLAlchemy Select object with the applied filters.
        """
        return select(
            self.model_class
        ).filter_by(
            **filters
        )

    async def count_filter_query(self, query: Select) -> int:
        """
        Count the number of records that match the given filter query.

        Args:
            - query (Select): The SQLAlchemy Select object with the applied filters.

        Returns:
            - int: The count of records that match the filter query.
        """
        count_query = select(
            func.count()
        ).select_from(
            query.subquery()
        )

        result = await self.db.execute(count_query)
        return int(result.scalar())

    async def execute_filter_query(self, query: Select) -> Sequence[T]:
        """
        Execute the given filter query and return the results.

        Args:
            - query (Select): The SQLAlchemy Select object with the applied filters.

        Returns:
            - Sequence[T]: A list of filtered model instances.
        """
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_paginated[Schema: BaseModel](
        self,
        paginator: Paginator,
        query_params: BaseModel,
        response_schema: Schema,
        **filters
    ) -> Generic[Schema]:
        """
        Retrieves and returns a paginated response based on the provided filters and query parameters.

        This asynchronous method constructs a filtered query using the given filters,
        counts the total number of matching records, paginates the results using the paginator,
        executes the query, and returns a paginated response formatted according to the specified schema.

        Args:
            - paginator (Paginator): A paginator class responsible for applying pagination logic to the query and response.
            - query_params (BaseModel): Query parameters used to control pagination and other query-related options.
            - response_schema (Schema): A Pydantic model that defines the structure of the paginated response.
            - **filters: Arbitrary keyword arguments used to filter the dataset before pagination.

        Returns:
            - Generic[Schema]: A paginated response object containing the filtered results and pagination metadata,
              structured according to the specified `response_schema`.
        """
        filter_query = self.get_filter_query(**filters)

        total_query_count = await self.count_filter_query(filter_query)

        paginated_query = paginator.paginate_query(
            query=filter_query,
            query_params=query_params,
        )

        results = await self.execute_filter_query(query=paginated_query)

        paginated_response = paginator.paginate_response(
            results=results,
            total_count=total_query_count,
            query_params=query_params,
            response_schema=response_schema
        )

        return paginated_response

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

        if obj is not None:
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
