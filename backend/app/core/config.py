# geoprumo/backend/app/core/config.py

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

class Settings(BaseSettings):
    """
    Define e carrega as configurações e chaves de API da aplicação.
    O Pydantic automaticamente lê as variáveis de ambiente com estes nomes.
    """
    # Chaves de API de serviços externos
    ORS_API_KEY: str = os.getenv("ORS_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    AI_PASSWORD: str = os.getenv("AI_PASSWORD", "")

    # Configurações da API do OpenRouteService
    ORS_BASE_URL: str = "https://api.openrouteservice.org"

    # Configurações da API do Google Gemini
    GEMINI_MODEL_NAME: str = "gemini-1.5-flash-latest"

    class Config:
        # Aponta para o arquivo .env que criamos na raiz do backend
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Cria uma instância única das configurações que será usada em toda a aplicação
settings = Settings()