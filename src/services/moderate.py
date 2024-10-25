from abc import ABC, abstractmethod

from src.services.ai_service import ai_response


class ModerateService(ABC):

    @abstractmethod
    async def includes_profanity(self, text: str) -> bool:
        raise NotImplementedError


class AIModerateService(ModerateService):
    async def includes_profanity(self, text: str) -> bool:
        prompt = (f"Does the following content contain inappropriate or obscene language? '{text}'"
                  f"Simply answer 'yes' or 'no'")
        response = await ai_response.get_response(prompt=prompt)
        return "yes" in response.lower()


moderate_service: ModerateService = AIModerateService()
