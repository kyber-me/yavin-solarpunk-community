from pydantic import BaseModel

# DataT = TypeVar("DataT")


class ApiError(BaseModel):
    code: str
    message: str
    details: object | None = None


class ApiResponse[DataT](BaseModel):
    data: DataT | None = None
    error: ApiError | None = None
