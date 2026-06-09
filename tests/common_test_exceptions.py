from fastapi_easy_responses.exceptions import CustomAppException


class DuplicateItemError(CustomAppException):
    status_code = 409
    description = "Duplicate item already exists"


class DynamicItemNotFoundError(CustomAppException):
    status_code = 404
    description = "Item not found"

    def __init__(self, item_id: int):
        self.detail = f"Item with ID {item_id} not found"
