from fastapi_easy_responses import CustomAppException, ErrorResponse, get_responses


class DuplicateItemError(CustomAppException):
    status_code = 409
    description = "Duplicate item already exists"


def test_get_responses_returns_registered_error_metadata():
    responses = get_responses(DuplicateItemError)

    assert 409 in responses
    assert responses[409]["description"] == "Duplicate item already exists"
    assert responses[409]["model"] is ErrorResponse


def test_get_responses_ignores_unregistered_exceptions():
    class SomeOtherError(Exception):
        pass

    assert get_responses(SomeOtherError) == {}
