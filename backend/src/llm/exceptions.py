from fastapi import HTTPException, status


class LLMUnavailable(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The language model service is unavailable. Try again shortly.",
        )
