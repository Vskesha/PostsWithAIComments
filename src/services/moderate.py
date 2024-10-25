from abc import ABC, abstractmethod

from src.services.ai import ai_service


class ModerateService(ABC):

    @abstractmethod
    async def includes_profanity(self, text: str) -> bool:
        raise NotImplementedError


class AIModerateService(ModerateService):
    async def includes_profanity(self, text: str) -> bool:
        prompt = (f"Does the following content contain inappropriate or obscene language? '{text}'"
                  f"Simply answer 'yes' or 'no'")
        response = await ai_service.get_response(prompt=prompt)
        return "yes" in response.lower()


moderate_service: ModerateService = AIModerateService()
