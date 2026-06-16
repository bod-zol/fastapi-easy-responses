# FastAPI Easy Responses

A simple package to easily handle and document all HTTP exceptions and other errors in a FastAPI app.

## Installation

```bash
uv add fastapi-easy-responses
```

```bash
pip install fastapi-easy-responses
```

## Usage

```python
# main
from fastapi_easy_responses import register_custom_exceptions
app = FastAPI()
register_custom_exceptions(app) # 1.

# exceptions
from fastapi_easy_responses import CustomAppException
class DuplicateItemError(CustomAppException): # 2.
    status_code = 409
    description = "An item with this name already exists."

# crud
async def create_item(session: AsyncSession, item: Item) -> Item:
    try:
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item
    except IntegrityError as e:
        await session.rollback()
        raise DuplicateItemError() from e # 3.

# router
from fastapi_easy_responses import get_responses
@router.post(
    "",
    response_model=ItemRead,
    status_code=201,
    responses=get_responses(DuplicateItemError), # 4.
)
async def create_item_endpoint(item: ItemCreate, session: AsyncSession):
    db_item = Item.model_validate(item)
    return await create_item(session, db_item) # 5.
```

This gives you a centralized, more consistent and easier-to-maintain exception handling and documentation.

Note the following:

  1. Call `register_custom_exceptions(app)` to activate the centralized exception handler for `CustomAppException`s.
  1. Inherit your exception class from `CustomAppException`, and provide the required `status_code` and `description` as class variables: as such, these are static per exception class, not dynamic per raise.
  1. Raise your exception in any operation.
  1. Use the same exception class to generate the OpenAPI documentation. No magic numbers and strings needed, so you have proper autocomplete.
  1. No need to manually catch and convert your exception to HTTPException, the centralized exception handler does it for you. Or more precisely, it returns the same JSONResponse as the default exception handler for HTTPException would.

This package doesn't introduce new response schemas or custom error codes, so adoption is easy: the exact same response is returned as with the pure FastAPI implementation, so you don't have to worry about rewriting your other services or frontend.

### Result

If you open the documentation, you'll see the following:

![Documentation sample](./docs/sample-doc.png)

And if you try it out, you'll see the actual response matches the documentation as expected:

![Response sample](./docs/sample-response.png)

### Dynamic detail

By default the response will contain the static description of the exception, which is usually enough.

But you can also provide the `detail` parameter to the base `CustomAppException` class, which will be used in the response instead of the static description if present.

Example:

```python
class ItemNotFoundError(CustomAppException):
    status_code = 404
    description = "Item not found"

    def __init__(self, item_id: int):
        super().__init__(detail=f"Item with ID {item_id} not found")

# Raise with dynamic detail
raise ItemNotFoundError(123)

# Use in documentation as usual
@router.get(
    "/{item_id}", response_model=ItemRead, responses=get_responses(ItemNotFoundError)
)
```

In this case, the documentation will still show the static description:

![Documentation sample](./docs/sample-dynamic-doc.png)

But the actual response will contain the dynamic detail:

![Response sample](./docs/sample-dynamic-response.png)

### Headers

You can also include custom headers in your responses by providing the `headers` parameter to the base `CustomAppException` class. This allows you to specify headers that should be included in the response when the exception is raised.

For documentation purposes, you can also define a `header_descriptions` attribute in your exception class. You can use anything here that you would normally use directly in the `responses` parameter of your route decorator.

Example:

```python
class UnauthorizedError(CustomAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    description = "Invalid credentials"
    header_descriptions = {
        "WWW-Authenticate": {
            "description": "Available authentication methods",
            "schema": {"type": "string"},
        }
    }

    def __init__(self):
        super().__init__(headers={"WWW-Authenticate": "Bearer"})

# Raise where appropriate
raise UnauthorizedError()

# Use in documentation as usual
@router.get("/me", responses=get_responses(UnauthorizedError))
```

In this case, the documentation will show the given header descriptions:

![Documentation sample](./docs/sample-header-doc.png)

And the actual response will contain the given headers:

![Response sample](./docs/sample-header-response.png)

## Why

For comparison, this is something like what you would usually do in a FastAPI app.

```python
# exceptions
class DuplicateItemError(ValueError):
    pass

# crud
async def create_item(session: AsyncSession, item: Item) -> Item:
    try:
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item
    except IntegrityError as e:
        await session.rollback()
        raise DuplicateItemError("An item with this name already exists.") from e

# router
@router.post(
    "",
    response_model=ItemRead,
    status_code=201,
    responses={
        409: {"model": Message, "description": "An item with this name already exists."}
    }
)
async def create_item_endpoint(item: ItemCreate, session: AsyncSession):
    try:
        db_item = Item.model_validate(item)
        return await create_item(session, db_item)
    except DuplicateItemError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
```

Which means

- You have to manually maintain all the thrown exception to HTTPException mappings. If you forget it, your unhandled exception will raise a generic internal server error.
- It also requires additional manual work to provide consistent documentation.

## Similar packages

There are similar packages with similar purpose, like

- [APIException](https://github.com/akutayural/APIException)
- [fastapi-problem](https://github.com/NRWLDev/fastapi-problem)

This package is simpler for basic use-cases, which may or may not be what you want. This package doesn't introduce new response schemas or custom error codes, doesn't provide logging (yet); but gives you the least amount of code you have to write to achieve the same functionality.

## License

[MIT](/LICENSE.md)
