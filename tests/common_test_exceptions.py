from fastapi_easy_responses.exceptions import (
    CustomAppException,
    HeaderDescription,
    ResponseHeaderSchema,
)


class DuplicateItemError(CustomAppException):
    status_code = 409
    description = "Duplicate item already exists"


class DynamicItemNotFoundError(CustomAppException):
    status_code = 404
    description = "Item not found"

    def __init__(self, item_id: int):
        super().__init__(detail=f"Item with ID {item_id} not found")


class ErrorWithHeader(CustomAppException):
    status_code = 401
    description = "Invalid credentials"
    header_descriptions = {
        "WWW-Authenticate": HeaderDescription(
            description="Available authentication methods",
            schema=ResponseHeaderSchema(type="string"),
        )
    }

    def __init__(self):
        super().__init__(
            headers={"WWW-Authenticate": "Bearer"},
        )
