from fastapi import HTTPException, status


class Forbidden(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ObjectNotFound(HTTPException):
    def __init__(self, detail: str = "Object not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConstrainError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
