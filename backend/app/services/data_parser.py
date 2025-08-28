# geoprumo/backend/app/services/data_parser.py

import pandas as pd
import os
import re
import requests
import io
import gpxpy
from lxml import etree
from typing import Dict, Any, Optional, Tuple, List, Union

from app.core.utils import haversine_distance

class DataParser:
    """
    Classe responsável por carregar, analisar, limpar e processar dados
    de diversas fontes (arquivos, links, texto).
    """

    def _parse_gpx(self, file_content: bytes) -> pd.DataFrame:
        """Analisa o conteúdo de um arquivo GPX para extrair os waypoints."""
        points = []
        try:
            gpx = gpxpy.parse(file_content.decode('utf-8'))
            for waypoint in gpx.waypoints:
                points.append({
                    "Nome": waypoint.name or "Waypoint GPX",
                    "Latitude": waypoint.latitude,
                    "Longitude": waypoint.longitude
                })
            return pd.DataFrame(points)
        except Exception as e:
            print(f"ERRO ao analisar GPX: {e}")
            return pd.DataFrame()

    def _parse_kml(self, file_content: bytes) -> pd.DataFrame:
        """Extrai pontos de uma estrutura KML."""
        points = []
        try:
            parser = etree.XMLParser(recover=True)
            tree = etree.fromstring(file_content, parser=parser)
            ns = {'kml': 'http://www.opengis.net/kml/2.2'}
            for placemark in tree.xpath('.//kml:Placemark', namespaces=ns):
                name = placemark.findtext('kml:name', default="Ponto KML", namespaces=ns).strip()
                coords_text = placemark.findtext('.//kml:coordinates', default="", namespaces=ns).strip()
                if coords_text:
                    coords = coords_text.split(',')
                    if len(coords) >= 2:
                        points.append({
                            "Nome": name,
                            "Latitude": float(coords[1]),
                            "Longitude": float(coords[0])
                        })
            return pd.DataFrame(points)
        except Exception as e:
            print(f"ERRO ao analisar KML: {e}")
            return pd.DataFrame()

    def _parse_csv_or_excel(self, file_content: bytes, is_excel: bool) -> pd.DataFrame:
        """Lê o conteúdo de um arquivo CSV ou XLSX."""
        try:
            if is_excel:
                return pd.read_excel(io.BytesIO(file_content))
            else:
                try:
                    text_content = file_content.decode('utf-8')
                except UnicodeDecodeError:
                    text_content = file_content.decode('latin-1')
                return pd.read_csv(io.StringIO(text_content), on_bad_lines='skip', sep=None, engine='python')
        except Exception as e:
            print(f"ERRO ao ler planilha: {e}")
            return pd.DataFrame()

    def _validate_coordinates(self, latitude: Any, longitude: Any) -> bool:
        """Verifica se um par de coordenadas é geograficamente válido."""
        try:
            return -90 <= float(latitude) <= 90 and -180 <= float(longitude) <= 180
        except (ValueError, TypeError):
            return False

    def _auto_detect_and_standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Tenta detectar e padronizar colunas de Interesse com uma lista de sinônimos robusta."""
        df_copy = df.copy()
        rename_map = {}
        
        # CORREÇÃO: Lista de sinônimos muito mais completa
        keywords = {
            'Latitude': ['latitude', 'lat', 'lat.', 'latitude (wgs84)'],
            'Longitude': ['longitude', 'lon', 'lng', 'long.', 'longitude (wgs84)'],
            'Nome': ['nome', 'name', 'título', 'ref', 'referencia', 'referência', 'ponto', 'local', 'faixa', 'ponto de bloqueio', 'ponto_de_bloqueio'],
            'Link': ['link', 'url', 'gmaps', 'maps'],
            'Observations': ['obs', 'observacoes', 'observações', 'desc', 'descricao', 'descrição']
        }
        
        df_cols_lower = {str(c).lower().strip(): c for c in df_copy.columns}

        for standard_name, kws in keywords.items():
            if standard_name not in df_copy.columns:
                for kw in kws:
                    if kw in df_cols_lower:
                        original_col_name = df_cols_lower[kw]
                        rename_map[original_col_name] = standard_name
                        break
        if rename_map:
            df_copy.rename(columns=rename_map, inplace=True)
        
        if 'Observations' in df_copy.columns:
            df_copy.rename(columns={'Observations': 'observations'}, inplace=True)

        return df_copy

    def clean_and_validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Orquestra a limpeza e validação de um DataFrame."""
        if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
            for col in df.columns:
                if df[col].dtype == 'object':
                    coords_series = df[col].dropna().astype(str).apply(self.extract_coords_from_text)
                    if not coords_series.dropna().empty and coords_series.count() / len(df[col].dropna()) > 0.5:
                        df['Latitude'] = coords_series.apply(lambda x: x[0] if x else None)
                        df['Longitude'] = coords_series.apply(lambda x: x[1] if x else None)
                        break

        if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
            return pd.DataFrame()

        df_clean = df.copy()

        def clean_coord_string(coord):
            if isinstance(coord, str):
                return re.sub(r"[°'\"NnSsOoWwEe\s]", "", coord).replace(',', '.')
            return coord

        for col in ['Latitude', 'Longitude']:
            df_clean[col] = df_clean[col].apply(clean_coord_string)
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

        df_clean.dropna(subset=['Latitude', 'Longitude'], inplace=True)

        valid_coords = df_clean.apply(
            lambda row: self._validate_coordinates(row['Latitude'], row['Longitude']),
            axis=1
        )
        return df_clean[valid_coords].reset_index(drop=True)

    def _fetch_link_content(self, url: str, allow_redirects: bool = True) -> Optional[bytes]:
        """Baixa o conteúdo de uma URL."""
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15, allow_redirects=allow_redirects)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            print(f"Falha ao buscar URL {url}: {e}")
            return None

    def parse_mymaps_link(self, url: str) -> pd.DataFrame:
        """Baixa e processa pontos de um link do Google My Maps."""
        mid_match = re.search(r"mid=([a-zA-Z0-9_-]+)", url)
        if not mid_match: return pd.DataFrame()
        
        mid = mid_match.group(1)
        kml_export_url = f"https://www.google.com/maps/d/kml?mid={mid}&forcekml=1"
        kml_content = self._fetch_link_content(kml_export_url)
        return self._parse_kml(kml_content) if kml_content else pd.DataFrame()

    def extract_coords_from_text(self, text: str) -> Optional[Tuple[float, float]]:
        """Extrai um par de latitude e longitude de uma string."""
        if not isinstance(text, str): return None
        text = text.strip()
        at_match = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", text)
        if at_match:
            lat, lon = float(at_match.group(1)), float(at_match.group(2))
            if self._validate_coordinates(lat, lon): return lat, lon
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
        if len(numbers) >= 2:
            try:
                c1, c2 = float(numbers[0]), float(numbers[1])
                if self._validate_coordinates(c1, c2): return c1, c2
                if self._validate_coordinates(c2, c1): return c2, c1
            except (ValueError, IndexError):
                pass
        return None