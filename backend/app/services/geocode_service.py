# geoprumo/backend/app/services/geocode_service.py

import requests
from typing import Optional, Tuple, List

from app.core.config import settings

class GeocodeService:
    """
    Serviços para geocodificação e autocompletar endereços usando OpenRouteService.
    """
    def geocode_address(self, address: str) -> Optional[Tuple[float, float, str]]:
        """
        Converte um endereço de texto em coordenadas geográficas (latitude, longitude)
        e retorna também o nome completo (label) encontrado.
        """
        if not settings.ORS_API_KEY:
            raise ConnectionError("A chave da API do OpenRouteService (ORS_API_KEY) não está configurada.")
        
        try:
            params = {"text": address, "size": 1}
            headers = {"Authorization": settings.ORS_API_KEY}
            response = requests.get(f"{settings.ORS_BASE_URL}/geocode/search", headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and data.get("features"):
                feature = data["features"][0]
                coords = feature["geometry"]["coordinates"]
                label = feature["properties"].get("label", address)
                return coords[1], coords[0], label
            else:
                return None
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Falha de conexão na geocodificação: {e}")
        except (KeyError, IndexError) as e:
            raise ValueError(f"A resposta da API de geocodificação está em um formato inesperado: {e}")

    # NOVA FUNÇÃO PARA AUTOCOMPLETAR
    def autocomplete_address(self, text: str) -> List[str]:
        """
        Busca sugestões de endereço (incluindo CEP) usando a API de autocomplete.
        """
        if not settings.ORS_API_KEY or len(text) < 3:
            return []
        
        try:
            # Foco em Belo Horizonte para resultados mais relevantes
            params = {
                "text": text,
                "focus.point.lon": -43.9333,
                "focus.point.lat": -19.9167,
            }
            headers = {"Authorization": settings.ORS_API_KEY}
            
            response = requests.get(f"{settings.ORS_BASE_URL}/geocode/autocomplete", headers=headers, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if data and data.get("features"):
                return [feature["properties"]["label"] for feature in data["features"]]
            else:
                return []
        except requests.exceptions.RequestException:
            return [] # Em caso de falha de conexão, retorna lista vazia
        except (KeyError, IndexError):
            return [] # Em caso de formato inesperado, retorna lista vazia