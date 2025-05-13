from typing import Protocol, Sequence

from sqlalchemy.orm.query import Query
from pydantic import BaseModel
from pydantic.generics import GenericModel
from shared_utils.db.base import Base


class Paginator[Model: Base, QueryParams: BaseModel, Schema: BaseModel, Response: GenericModel[Schema]](Protocol):
    """
    Protocol for a paginator that handles pagination logic for a given model.
    This protocol defines the methods required for paginating a query and formatting the response.
    """

    @staticmethod
    def paginate_query(
        query: Query[Model],
        query_params: QueryParams,
    ) -> Query[Model]:
        """
        Paginate a SQLAlchemy query based on the provided query parameters.

        Args:
            - query (Query[Model]): The SQLAlchemy query to paginate.
            - query_params (QueryParams): The parameters for pagination.

        Returns:
            - Query[Model]: The paginated SQLAlchemy query.
        """
        ...

    @staticmethod
    def paginate_response(
        results: Sequence[Model],
        total_count: int,
        page_params: QueryParams,
        response_schema: Schema,
    ) -> Response:
        """
        Format the paginated results into a response schema.

        Args:
            - results (Sequence[Model]): The results of the paginated query.
            - total_count (int): The total number of items in the query.
            - page_params (QueryParams): The parameters used for pagination.
            - response_schema (Schema): The schema to format the response.

        Returns:
            - Response: The formatted paginated response.
        """
        ...
