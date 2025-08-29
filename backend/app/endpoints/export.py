# geoprumo/backend/app/endpoints/export.py

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import Response
from typing import List

# --- Importações ---
from app.models.schemas import Point # Reutilizamos o schema de Ponto
from app.services.exporter import Exporter

# --- Configuração ---
router = APIRouter(
    prefix="/api/v1/export",
    tags=["Exportação de Rotas"]
)
exporter = Exporter()

@router.post("/{file_format}")
def export_route(file_format: str, points: List[Point] = Body(...)):
    """
    Endpoint genérico para exportar uma rota para diferentes formatos.
    Recebe a lista de pontos e o formato desejado (csv, kml, gpx, geojson, mymaps).
    """
    if not points:
        raise HTTPException(status_code=400, detail="A lista de pontos não pode estar vazia.")

    points_dict = [p.dict() for p in points]

    if file_format == "csv":
        content = exporter.to_csv(points_dict)
        return Response(content=content, media_type="text/csv", headers={'Content-Disposition': 'attachment; filename=rota_otimizada.csv'})
    
    elif file_format == "kml":
        content = exporter.to_kml(points_dict)
        return Response(content=content, media_type="application/vnd.google-earth.kml+xml", headers={'Content-Disposition': 'attachment; filename=rota_otimizada.kml'})

    elif file_format == "gpx":
        content = exporter.to_gpx(points_dict)
        return Response(content=content, media_type="application/gpx+xml", headers={'Content-Disposition': 'attachment; filename=rota_otimizada.gpx'})

    elif file_format == "geojson":
        content = exporter.to_geojson(points_dict)
        return Response(content=content, media_type="application/geo+json", headers={'Content-Disposition': 'attachment; filename=rota_otimizada.geojson'})

    elif file_format == "mymaps":
        content = exporter.to_mymaps_csv(points_dict)
        return Response(content=content, media_type="text/csv", headers={'Content-Disposition': 'attachment; filename=rota_para_mymaps.csv'})

    else:
        raise HTTPException(status_code=404, detail=f"Formato de arquivo '{file_format}' não suportado.")


@router.post("/google-maps-links", response_model=List[str])
def get_google_maps_links(points: List[Point] = Body(...)):
    """
    Gera e retorna uma lista de URLs do Google Maps para a rota otimizada.
    """
    if not points:
        raise HTTPException(status_code=400, detail="A lista de pontos não pode estar vazia.")

    try:
        points_dict = [p.dict() for p in points]
        urls = exporter.generate_google_maps_links(points_dict)
        return urls
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar links do Google Maps: {e}")