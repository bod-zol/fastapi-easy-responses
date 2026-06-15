from common_test_exceptions import (
    DuplicateItemError,
    DynamicItemNotFoundError,
    ErrorWithHeader,
)
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from fastapi_easy_responses import (
    CustomAppException,
    get_responses,
    register_custom_exceptions,
)


def create_app(*, to_throw: CustomAppException) -> FastAPI:
    app = FastAPI()
    register_custom_exceptions(app)

    @app.post("/items", responses=get_responses(to_throw.__class__))
    def create_item():
        raise to_throw

    return app


def create_reference_app(*, to_throw: HTTPException) -> FastAPI:
    app = FastAPI()

    @app.post("/items")
    def create_item():
        raise to_throw

    return app


def test_app_returns_json_response_for_custom_exception():
    client = TestClient(create_app(to_throw=DuplicateItemError()))

    response = client.post("/items")

    assert response.status_code == 409
    assert response.json() == {"detail": "Duplicate item already exists"}


def test_app_returns_json_response_for_custom_exception_with_custom_detail():
    client = TestClient(create_app(to_throw=DynamicItemNotFoundError(item_id=123)))

    response = client.post("/items")

    assert response.status_code == 404
    assert response.json() == {"detail": "Item with ID 123 not found"}


def test_app_returns_same_response_as_default_fastapi_handler_for_custom_exception():
    ref_client = TestClient(
        create_reference_app(
            to_throw=HTTPException(
                status_code=409, detail="Duplicate item already exists"
            )
        )
    )
    test_client = TestClient(create_app(to_throw=DuplicateItemError()))

    ref_response = ref_client.post("/items")
    test_response = test_client.post("/items")

    assert ref_response.status_code == test_response.status_code
    assert ref_response.json() == test_response.json()


def test_exception_returns_headers():
    client = TestClient(create_app(to_throw=ErrorWithHeader()))

    response = client.post("/items")

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}
    assert response.headers.get("WWW-Authenticate") == "Bearer"
