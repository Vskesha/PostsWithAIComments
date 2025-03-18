from abc import ABC, abstractmethod

import vertexai
from google.oauth2.service_account import Credentials
from vertexai.generative_models import GenerativeModel

from src.conf.config import settings

service_account_info = {
    "type": settings.google_sa_type,
    "project_id": settings.google_sa_project_id,
    "private_key_id": settings.google_sa_private_key_id,
    "private_key": settings.google_sa_private_key,
    "client_email": settings.google_sa_client_email,
    "client_id": settings.google_sa_client_id,
    "auth_uri": settings.google_sa_auth_uri,
    "token_uri": settings.google_sa_token_uri,
    "auth_provider_x509_cert_url": settings.google_sa_auth_provider_x509_cert_url,
    "client_x509_cert_url": settings.google_sa_client_x509_cert_url,
    "universe_domain": settings.google_sa_universe_domain,
}

credentials = Credentials.from_service_account_info(service_account_info)

vertexai.init(
    project=settings.google_sa_project_id,
    location=settings.google_sa_location,
    credentials=credentials,
)


class AIService(ABC):

    @abstractmethod
    async def get_response(self, prompt: str) -> str:
        raise NotImplementedError


class GeminiService(AIService):
    model = GenerativeModel("gemini-1.5-flash-002")

    async def get_response(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text


ai_service: AIService = GeminiService()
