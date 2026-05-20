from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_easy_responses import (
    CustomAppException,
    get_responses,
    register_custom_exceptions,
)


class DuplicateItemError(CustomAppException):
    status_code = 409
    description = "Duplicate item already exists"


def create_app() -> FastAPI:
    app = FastAPI()
    register_custom_exceptions(app)

    @app.post("/items", responses=get_responses(DuplicateItemError))
    def create_item():
        raise DuplicateItemError()

    return app


def test_custom_app_exception_handler_returns_json_response():
    client = TestClient(create_app())

    response = client.post("/items")

    assert response.status_code == 409
    assert response.json() == {"detail": "Duplicate item already exists"}
