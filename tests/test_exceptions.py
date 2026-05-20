from fastapi_easy_responses import CustomAppException, ErrorResponse, get_responses


class DuplicateItemError(CustomAppException):
    status_code = 409
    description = "Duplicate item already exists"


def test_get_responses_returns_registered_error_metadata():
    responses = get_responses(DuplicateItemError)

    assert len(responses) == 1
    assert 409 in responses
    assert responses[409]["description"] == "Duplicate item already exists"
    assert responses[409]["model"] is ErrorResponse


def test_get_responses_returns_multiple_registered_exceptions():
    class NotFoundError(CustomAppException):
        status_code = 404
        description = "Item not found"

    responses = get_responses(DuplicateItemError, NotFoundError)

    assert len(responses) == 2

    assert 409 in responses
    assert responses[409]["description"] == "Duplicate item already exists"
    assert responses[409]["model"] is ErrorResponse

    assert 404 in responses
    assert responses[404]["description"] == "Item not found"
    assert responses[404]["model"] is ErrorResponse


def test_get_responses_returns_empty_dict_for_no_exceptions():
    assert get_responses() == {}


def test_get_responses_ignores_unregistered_exceptions():
    class SomeOtherError(Exception):
        pass

    assert get_responses(SomeOtherError) == {}
