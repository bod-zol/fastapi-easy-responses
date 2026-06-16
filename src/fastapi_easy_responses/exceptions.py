from collections.abc import Mapping

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standardized error response model."""

    detail: str


class CustomAppException(Exception):
    """Base class for custom application exceptions with HTTP metadata.

    Subclasses should have their `status_code`, `description` and `headers_descriptions`
    class attributes set. These will automatically get registered upon definition.

    A subclass may optionally include a `detail` attribute for dynamic error messages,
    which will be used in the actual response instead of the static description.

    Also, a subclass can include a `headers` attribute for dynamic response headers,
    which will be included in the response.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    description: str = "Internal server error"
    header_descriptions: dict[str, dict[str, object]] | None = None

    registry: dict[str, dict[str, object]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls is not CustomAppException:
            entry: dict[str, object] = {
                "status_code": cls.status_code,
                "description": cls.description,
            }
            if getattr(cls, "header_descriptions", None):
                entry["header_descriptions"] = cls.header_descriptions
            CustomAppException.registry[cls.__name__] = entry

    def __init__(
        self,
        *,
        detail: str | None = None,
        headers: Mapping[str, str] | None | None = None,
    ):
        if detail is not None:
            self.detail = detail
        if headers is not None:
            self.headers = headers


def register_custom_exceptions(app: FastAPI) -> None:
    """Register exception handlers for CustomAppException subclasses
    using FastAPI's decorator.

    This function should be called in the main application setup to ensure
    that all custom exceptions are properly handled.
    """

    @app.exception_handler(CustomAppException)
    async def custom_app_exception_handler(
        request: Request, exc: CustomAppException
    ) -> JSONResponse:
        """Convert CustomAppException to JSONResponse with appropriate status code."""
        detail = getattr(exc, "detail", exc.description)
        headers = getattr(exc, "headers", None)
        if headers:
            assert isinstance(headers, dict), "Headers must be a dictionary"
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(detail=detail).model_dump(),
            headers=headers,
        )


def get_responses(*exception_classes: type[Exception]) -> dict:
    """
    Auto-generate FastAPI response documentation from exception registry.

    Remarks:
     - Handles only exceptions that are subclasses of CustomAppException.
     - If multiple exceptions share the same status code,
       only the last one will be documented for that code.

    Usage:
        @router.post("...", responses=get_responses(DuplicateItemError))
        async def my_endpoint(...): ...
    """
    responses = {}
    for exc_cls in exception_classes:
        exc_name = exc_cls.__name__
        if exc_name in CustomAppException.registry:
            exc_info = CustomAppException.registry[exc_name]
            one_response = {
                "description": exc_info["description"],
                "model": ErrorResponse,
            }
            if exc_info.get("header_descriptions"):
                one_response["headers"] = exc_info["header_descriptions"]
            responses[exc_info["status_code"]] = one_response
    return responses
