# geoprumo/backend/app/endpoints/geocode.py

from fastapi import APIRouter, HTTPException, Query
from typing import List

from app.services.geocode_service import GeocodeService
from app.services.data_parser import DataParser

router = APIRouter(
    prefix="/api/v1/geocode",
    tags=["Geocodificação"]
)
geocode_service = GeocodeService()
parser = DataParser()

@router.get("/search")
def search_address(q: str = Query(..., min_length=3)):
    """
    Recebe um texto (q), tenta extrair coordenadas diretas.
    Se não conseguir, usa a geocodificação para encontrar o endereço.
    """
    coords = parser.extract_coords_from_text(q)
    if coords:
        return { "name": q, "latitude": coords[0], "longitude": coords[1] }
    
    try:
        result = geocode_service.geocode_address(q)
        if result:
            lat, lon, name = result
            return { "name": name, "latitude": lat, "longitude": lon }
        else:
            raise HTTPException(status_code=404, detail=f"Não foi possível encontrar o endereço para: '{q}'")
    except (ConnectionError, ValueError) as e:
        raise HTTPException(status_code=500, detail=str(e))

# NOVO ENDPOINT DE AUTOCOMPLETE
@router.get("/autocomplete", response_model=List[str])
def autocomplete_address_search(q: str = Query(..., min_length=3)):
    """
    Fornece sugestões de endereço em tempo real com base na entrada do usuário.
    """
    try:
        suggestions = geocode_service.autocomplete_address(q)
        return suggestions
    except Exception as e:
        # Retorna uma lista vazia em caso de erro no servidor
        print(f"Erro no autocomplete: {e}")
        return []