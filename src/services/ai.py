from abc import ABC, abstractmethod


class AIService(ABC):

    @abstractmethod
    async def get_response(self, prompt: str) -> str:
        raise NotImplementedError


class GeminiService(AIService):

    async def get_response(self, prompt: str) -> str:
        return ""


ai_service: AIService = GeminiService()
