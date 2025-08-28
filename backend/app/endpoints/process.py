# geoprumo/backend/app/endpoints/process.py

from fastapi import APIRouter, HTTPException, Body
import pandas as pd
import base64
import re
from typing import List

# --- Importações ---
from app.models.schemas import ProcessRequest, ProcessResponse, Point, SummaryOutput, EnrichRequest
from app.services.data_parser import DataParser
from app.services.optimizer import RouteOptimizer
from app.services.ai_services import AIServices

# --- Configuração ---
router = APIRouter(
    prefix="/api/v1/process",
    tags=["Processamento e Otimização"]
)
parser = DataParser()
optimizer = RouteOptimizer()

@router.post("/optimize", response_model=ProcessResponse)
def optimize(request: ProcessRequest = Body(...)):
    """
    Endpoint para análise, limpeza e otimização de rota.
    Consolida os pontos existentes com os novos dados de forma robusta.
    """
    try:
        all_dfs = []

        if request.existing_points:
            existing_points_data = [p.dict() for p in request.existing_points]
            df_existing = pd.DataFrame(existing_points_data)
            df_existing.rename(columns={'name': 'Nome', 'latitude': 'Latitude', 'longitude': 'Longitude', 'observations': 'Observations'}, inplace=True)
            all_dfs.append(df_existing)

        # Processar Arquivos
        for file_input in request.files:
            content_bytes = base64.b64decode(file_input.content)
            df = pd.DataFrame()
            if file_input.filename.lower().endswith(('.csv', '.xlsx')): df = parser._parse_csv_or_excel(content_bytes, is_excel=file_input.filename.lower().endswith('.xlsx'))
            elif file_input.filename.lower().endswith('.kml'): df = parser._parse_kml(content_bytes)
            elif file_input.filename.lower().endswith('.gpx'): df = parser._parse_gpx(content_bytes)
            if not df.empty: all_dfs.append(df)
        
        # Processar Links
        for link in request.links:
            df = pd.DataFrame()
            if re.search(r"mid=([a-zA-Z0-9_-]+)", link):
                df = parser.parse_mymaps_link(link)
            else: # Se não for My Maps, trata como um link de ponto único
                coords = parser.extract_coords_from_text(link)
                if coords:
                    df = pd.DataFrame([{"Nome": link, "Latitude": coords[0], "Longitude": coords[1]}])
            if not df.empty: all_dfs.append(df)

        # Processar Textos
        for text_input in request.texts:
            if text_input.strip():
                df = parser._parse_csv_or_excel(text_input.encode('utf-8'), is_excel=False)
                if not df.empty: all_dfs.append(df)
        
        if not all_dfs: raise HTTPException(status_code=400, detail="Nenhum dado válido encontrado para processar.")

        raw_df = pd.concat(all_dfs, ignore_index=True)
        if 'original_index' in raw_df.columns: raw_df = raw_df.drop(columns=['original_index'])
        raw_df.reset_index(inplace=True); raw_df.rename(columns={'index': 'original_index'}, inplace=True)

        standardized_df = parser._auto_detect_and_standardize_columns(raw_df)
        clean_df = parser.clean_and_validate_data(standardized_df)

        if clean_df.empty: raise HTTPException(status_code=400, detail="Nenhum ponto com coordenadas válidas foi encontrado.")

        optimization_result = optimizer.optimize_route(clean_df, mode=request.options.optimization_mode)
        optimized_df = optimization_result["data"].copy()
        
        column_mapping = {'Nome': 'name', 'Latitude': 'latitude', 'Longitude': 'longitude', 'observations': 'observations', 'original_index': 'original_index'}
        optimized_df.rename(columns={k: v for k,v in column_mapping.items() if k in optimized_df.columns}, inplace=True)
        
        if 'name' not in optimized_df.columns: optimized_df['name'] = [f"Ponto {i+1}" for i in range(len(optimized_df))]
        optimized_df['order'] = range(1, len(optimized_df) + 1)
        
        records = optimized_df.to_dict(orient='records')
        route_points = [Point(**{k: v for k, v in p.items() if pd.notna(v)}) for p in records]
        
        summary = None
        if "distance" in optimization_result and "duration" in optimization_result:
            summary = SummaryOutput(distance_km=optimization_result["distance"], duration_min=optimization_result["duration"])

        return ProcessResponse(
            status="success", message="Rota atualizada e reotimizada com sucesso!",
            optimized_route=route_points, summary=summary, map_geojson=optimization_result.get("geojson")
        )

    except (ConnectionError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Um erro inesperado ocorreu no servidor: {e}")

@router.post("/enrich-with-ai", response_model=List[Point])
def enrich_with_ai(request: EnrichRequest = Body(...)):
    try:
        ai_services = AIServices()
        points_data = [p.dict() for p in request.points]
        df = pd.DataFrame(points_data)
        df.rename(columns={'name': 'Nome', 'latitude': 'Latitude', 'longitude': 'Longitude'}, inplace=True)
        enriched_df = ai_services.enrich_data(df)
        final_df = ai_services.standardize_names(enriched_df)
        final_df.rename(columns={'Nome': 'name', 'address': 'address', 'category': 'category'}, inplace=True)
        return [Point(**p) for p in final_df.to_dict(orient='records')]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro no serviço de IA: {e}")