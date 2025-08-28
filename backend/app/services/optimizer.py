# geoprumo/backend/app/services/optimizer.py

import pandas as pd
import requests
from typing import Optional, Dict, Any

# --- Importações de bibliotecas de otimização ---
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# --- Importações de módulos do nosso projeto ---
from app.core.config import settings
from app.core.utils import haversine_distance

class RouteOptimizer:
    """
    Classe para orquestrar a otimização de rotas, tanto offline (OR-Tools)
    quanto online (OpenRouteService).
    """

    def _ortools_optimizer(self, df: pd.DataFrame, start_node: int, end_node: int) -> pd.DataFrame:
        """
        Otimiza a rota offline usando Google OR-Tools (Problema do Caixeiro Viajante).
        """
        if len(df) <= 2:
            return df

        coords = df[['Latitude', 'Longitude']].values.tolist()
        num_locations = len(coords)
        manager = pywrapcp.RoutingIndexManager(num_locations, 1, [start_node], [end_node])
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            lat1, lon1 = coords[from_node]
            lat2, lon2 = coords[to_node]
            return haversine_distance(lat1, lon1, lat2, lon2)

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.FromSeconds(5)

        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            route_indices = []
            index = routing.Start(0)
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route_indices.append(node_index)
                index = solution.Value(routing.NextVar(index))
            route_indices.append(manager.IndexToNode(index))
            
            return df.iloc[route_indices].reset_index(drop=True)
        else:
            print("Otimização offline (OR-Tools) não encontrou solução.")
            return df

    def _ors_optimizer(self, df: pd.DataFrame, start_node: int, end_node: int) -> Dict[str, Any]:
        """
        Otimiza a rota online usando a API do OpenRouteService.
        """
        if not settings.ORS_API_KEY:
            raise ConnectionError("A chave da API do OpenRouteService (ORS_API_KEY) não está configurada.")

        df_valid = df.dropna(subset=['Latitude', 'Longitude'])
        if len(df_valid) < 2:
            return {"data": df} # Retorna dados originais se não houver pontos suficientes

        coords = df_valid[["Longitude", "Latitude"]].values.tolist()
        
        jobs = [{"id": idx, "location": loc} for idx, loc in enumerate(coords) if idx not in [start_node, end_node]]
        vehicles = [{"id": 1, "profile": "driving-car", "start": coords[start_node], "end": coords[end_node]}]
        payload = {"jobs": jobs, "vehicles": vehicles}
        headers = {"Authorization": settings.ORS_API_KEY, "Content-Type": "application/json"}

        try:
            opt_response = requests.post(f"{settings.ORS_BASE_URL}/optimization", json=payload, headers=headers, timeout=30)
            opt_response.raise_for_status()
            opt_result = opt_response.json()

            steps = opt_result["routes"][0]["steps"]
            ordered_job_indices = [s["id"] for s in steps if s['type'] == 'job']
            final_route_indices = [start_node] + ordered_job_indices + [end_node]
            ordered_df = df_valid.iloc[final_route_indices].reset_index(drop=True)

            dir_payload = {"coordinates": ordered_df[["Longitude", "Latitude"]].values.tolist()}
            dir_response = requests.post(f"{settings.ORS_BASE_URL}/v2/directions/driving-car/geojson", json=dir_payload, headers=headers, timeout=30)
            dir_response.raise_for_status()
            dir_result = dir_response.json()

            summary = dir_result["features"][0]["properties"]["summary"]
            
            return {
                "data": ordered_df,
                "geojson": dir_result,
                "distance": summary["distance"] / 1000,
                "duration": summary["duration"] / 60
            }

        except requests.exceptions.RequestException as e:
            # CORREÇÃO: Levanta um erro específico que podemos tratar
            raise ConnectionError(f"Falha de conexão com a API do ORS: {e}")
        except (KeyError, IndexError, Exception) as e:
            # CORREÇÃO: Levanta um erro específico que podemos tratar
            raise ValueError(f"A API do ORS retornou um erro ou formato inesperado: {e}")

    def optimize_route(self, df: pd.DataFrame, mode: str, start_node_index: int = 0, end_node_index: int = -1) -> Dict[str, Any]:
        """
        Ponto de entrada principal para otimizar uma rota.
        """
        if df.empty or len(df) < 2:
            return {"data": df}

        if end_node_index == -1 or end_node_index >= len(df):
            end_node_index = len(df) - 1
            
        if mode == 'offline':
            optimized_df = self._ortools_optimizer(df, start_node_index, end_node_index)
            return {"data": optimized_df}
        
        elif mode == 'online':
            # A função _ors_optimizer agora levanta erros em vez de retornar None
            return self._ors_optimizer(df, start_node_index, end_node_index)

        else:
            raise ValueError(f"Modo de otimização desconhecido: {mode}")