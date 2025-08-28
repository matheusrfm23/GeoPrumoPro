# geoprumo/backend/app/models/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union # Importa Union

class FileInput(BaseModel):
    filename: str = Field(..., description="O nome original do arquivo.")
    content: str = Field(..., description="O conteúdo do arquivo codificado em Base64.")

class OptimizationOptions(BaseModel):
    optimization_mode: str = Field(default="online", description="Modo de otimização: 'online' ou 'offline'.")

class Point(BaseModel):
    order: int
    name: Optional[str] = "Ponto"
    latitude: float
    longitude: float
    address: Optional[str] = None
    category: Optional[str] = None
    original_index: Union[int, str] # CORREÇÃO: Tipo mais específico que 'Any'
    observations: Optional[str] = None
    active: Optional[bool] = True

class ProcessRequest(BaseModel):
    files: Optional[List[FileInput]] = Field(default=[], description="Lista de arquivos novos.")
    links: Optional[List[str]] = Field(default=[], description="Lista de links novos.")
    texts: Optional[List[str]] = Field(default=[], description="Lista de textos brutos novos.")
    existing_points: Optional[List[Point]] = Field(default=[], description="Lista de pontos já processados da rota atual.")
    options: OptimizationOptions = Field(default_factory=OptimizationOptions, description="Opções para a otimização.")

class EnrichRequest(BaseModel):
    points: List[Point]

class SummaryOutput(BaseModel):
    distance_km: float
    duration_min: float

class ProcessResponse(BaseModel):
    status: str
    message: str
    optimized_route: Optional[List[Point]] = None
    summary: Optional[SummaryOutput] = None
    map_geojson: Optional[Dict[str, Any]] = None