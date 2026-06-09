from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standardized error response model."""

    detail: str


class CustomAppException(Exception):
    """Base class for custom application exceptions with HTTP metadata.

    Subclasses should have their status_code and description class properties set.
    These will automatically get registered upon definition.

    A subclass may optionally include a `detail` attribute for dynamic error messages,
    which will be used in the response instead of the static description if present.
    Documentation will still use the static description.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    description: str = "Internal server error"

    registry: dict[str, dict[str, object]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls is not CustomAppException:
            CustomAppException.registry[cls.__name__] = {
                "status_code": cls.status_code,
                "description": cls.description,
            }


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
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(detail=detail).model_dump(),
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
            responses[exc_info["status_code"]] = {
                "description": exc_info["description"],
                "model": ErrorResponse,
            }
    return responses
