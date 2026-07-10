from typing import Annotated

from fastapi import Depends, Request

from src.llm.client import GeminiClient


async def get_llm(request: Request) -> GeminiClient:
    return request.app.state.llm


LLMClient = Annotated[GeminiClient, Depends(get_llm)]
