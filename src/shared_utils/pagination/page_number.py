from typing import Annotated, Optional, Sequence

from sqlalchemy.orm.query import Query
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from shared_utils.pagination.base import Paginator


class PageNumberPaginationQueryParams(BaseModel):
    """
    Parameters for page number pagination.
    This class defines the parameters required for paginating a query
    using page numbers and sizes.
    """
    page: Annotated[Optional[int], Field(ge=1)] = 1
    size: Annotated[Optional[int], Field(ge=1, le=101)] = 10


class PageNumberPaginationResponse[Schema: BaseModel](GenericModel):
    """
    Response model for page number pagination.
    This class defines the structure of the response returned after
    paginating a query using page numbers and sizes.
    """
    total_count: int
    next_page: Optional[int]
    previous_page: Optional[int]
    results: Optional[Sequence[Schema]]


class PageNumberPaginator[Model: BaseModel, Schema: BaseModel](
        Paginator[Model, PageNumberPaginationQueryParams, Schema: BaseModel, PageNumberPaginationResponse[Schema]]
    ):
    """
    Paginator for page number pagination.
    This class implements the Paginator protocol for handling pagination
    logic using page numbers and sizes.
    """

    @staticmethod
    def paginate_query(
        query: Query[Model],
        query_params: PageNumberPaginationQueryParams,
    ) -> Query[Model]:
        """
        Paginate a SQLAlchemy query based on the provided page number and size.

        Args:
            - query (Query[Model]): The SQLAlchemy query to paginate.
            - query_params (PageNumberPaginationQueryParams): The parameters for pagination.

        Returns:
            - Query[Model]: The paginated SQLAlchemy query.
        """

        return query.offset(
            (query_params.page - 1) * query_params.size
        ).limit(
            query_params.size
        )

    @staticmethod
    def paginate_response(
        results: Sequence[Model],
        total_count: int,
        query_params: PageNumberPaginationQueryParams,
        response_schema: Schema,
    ) -> PageNumberPaginationResponse[Schema]:
        """
        Format the paginated results into a response schema.

        Args:
            - results (Sequence[Model]): The results of the paginated query.
            - total_count (int): The total number of items in the query.
            - query_params (PageNumberPaginationQueryParams): The parameters used for pagination.
            - response_schema (Schema): The schema to format the response.

        Returns:
            - PageNumberPaginationResponse[Schema]: The formatted paginated response.
        """

        if not results:
            return PageNumberPaginationResponse(
                count=0,
                next_page=None,
                previous_page=None,
                results=[],
            )

        page_size = query_params.size
        current_page = query_params.page
        total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
        previous_page = current_page - 1 if current_page > 1 else None
        next_page = current_page + 1 if current_page < total_pages else None

        validated_results = [
            response_schema.model_validate(item) for item in results
        ]

        return PageNumberPaginationResponse(
            total_count=total_count,
            next_page=next_page,
            previous_page=previous_page,
            results=validated_results,
        )
