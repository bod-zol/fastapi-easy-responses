from fastapi import FastAPI, HTTPException
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


def test_app_returns_json_response_for_custom_exception():
    client = TestClient(create_app())

    response = client.post("/items")

    assert response.status_code == 409
    assert response.json() == {"detail": "Duplicate item already exists"}


def test_app_returns_same_response_as_default_fastapi_handler_for_custom_exception():
    def create_reference_app() -> FastAPI:
        app = FastAPI()

        @app.post("/items")
        def create_item():
            raise HTTPException(status_code=409, detail="Duplicate item already exists")

        return app

    ref_client = TestClient(create_reference_app())
    test_client = TestClient(create_app())

    ref_response = ref_client.post("/items")
    test_response = test_client.post("/items")

    assert ref_response.status_code == test_response.status_code
    assert ref_response.json() == test_response.json()
