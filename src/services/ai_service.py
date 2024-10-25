from abc import ABC, abstractmethod


class AIResponse(ABC):

    @abstractmethod
    async def get_response(self, prompt: str) -> str:
        raise NotImplementedError


class GeminiResponse(AIResponse):

    async def get_response(self, prompt: str) -> str:
        return ""


ai_response: AIResponse = GeminiResponse()