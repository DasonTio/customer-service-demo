from typing import Annotated

from fastapi import Depends, Request

from src.llm.client import OllamaClient


async def get_llm(request: Request) -> OllamaClient:
    return request.app.state.llm


LLMClient = Annotated[OllamaClient, Depends(get_llm)]
