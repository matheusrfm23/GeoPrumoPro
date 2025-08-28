# geoprumo/backend/app/services/exporter.py

import pandas as pd
import json
from lxml import etree
import gpxpy
from gpxpy.gpx import GPX, GPXWaypoint, GPXRoute, GPXRoutePoint
from typing import Dict, List, Any

# Importa a função corrigida
from app.core.utils import decimal_to_dms

class Exporter:
    """
    Classe responsável por converter um DataFrame de rota
    para diversos formatos de arquivo (CSV, KML, GPX, etc.).
    """
    def _prepare_dataframe(self, points: List[Dict[str, Any]]) -> pd.DataFrame:
        """Converte la lista de pontos em um DataFrame padronizado."""
        df = pd.DataFrame(points)
        cols = ['order', 'name', 'latitude', 'longitude', 'address', 'category', 'observations']
        df = df[[col for col in cols if col in df.columns]]
        df.rename(columns={
            'order': 'Ordem', 'name': 'Nome', 'latitude': 'Latitude', 
            'longitude': 'Longitude', 'address': 'Endereço', 'category': 'Categoria',
            'observations': 'Observações'
        }, inplace=True)
        return df

    def to_csv(self, points: List[Dict[str, Any]]) -> str:
        """Converte a rota para uma string no formato CSV."""
        df = self._prepare_dataframe(points)
        return df.to_csv(index=False, encoding='utf-8-sig')

    def to_geojson(self, points: List[Dict[str, Any]]) -> str:
        """Converte os pontos e a rota para uma string no formato GeoJSON."""
        df = self._prepare_dataframe(points)
        features = []
        for _, row in df.iterrows():
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [row['Longitude'], row['Latitude']]},
                "properties": { "name": row.get('Nome'), "order": row['Ordem'] }
            })
        
        line_coordinates = df[['Longitude', 'Latitude']].values.tolist()
        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": line_coordinates},
            "properties": {"name": "Rota Otimizada"}
        })
        geojson_output = {"type": "FeatureCollection", "features": features}
        return json.dumps(geojson_output, indent=2)

    def to_kml(self, points: List[Dict[str, Any]]) -> bytes:
        """Converte a rota para um arquivo KML em formato de bytes."""
        df = self._prepare_dataframe(points)
        kml_root = etree.Element("kml", nsmap={None: "http://www.opengis.net/kml/2.2"})
        document = etree.SubElement(kml_root, "Document")
        etree.SubElement(document, "name").text = "Rota Otimizada"
        
        for _, row in df.iterrows():
            placemark = etree.SubElement(document, "Placemark")
            etree.SubElement(placemark, "name").text = str(row.get('Nome'))
            point = etree.SubElement(placemark, "Point")
            etree.SubElement(point, "coordinates").text = f"{row['Longitude']},{row['Latitude']},0"
            
        placemark_route = etree.SubElement(document, "Placemark")
        etree.SubElement(placemark_route, "name").text = "Trajeto da Rota"
        line_string = etree.SubElement(placemark_route, "LineString")
        coords_text = " ".join([f"{row['Longitude']},{row['Latitude']},0" for _, row in df.iterrows()])
        etree.SubElement(line_string, "coordinates").text = coords_text
        
        return etree.tostring(kml_root, pretty_print=True, xml_declaration=True, encoding='utf-8')

    def to_gpx(self, points: List[Dict[str, Any]]) -> str:
        """Converte a rota para uma string no formato GPX."""
        df = self._prepare_dataframe(points)
        gpx = GPX()
        
        for _, row in df.iterrows():
            gpx.waypoints.append(GPXWaypoint(latitude=row['Latitude'], longitude=row['Longitude'], name=str(row.get('Nome'))))
            
        gpx_route = GPXRoute(name="Rota Otimizada")
        gpx_route.points = [GPXRoutePoint(row['Latitude'], row['Longitude']) for _, row in df.iterrows()]
        gpx.routes.append(gpx_route)
        
        return gpx.to_xml(prettyprint=True)

    def to_mymaps_csv(self, points: List[Dict[str, Any]]) -> str:
        """Formata a rota para um CSV compatível com o Google My Maps."""
        df = self._prepare_dataframe(points)
        df_mymaps = df.copy()

        df_mymaps['Coordenadas DMS'] = df_mymaps.apply(
            lambda row: f"{decimal_to_dms(row['Latitude'], is_lat=True)}, {decimal_to_dms(row['Longitude'], is_lat=False)}",
            axis=1
        )
        
        cols_to_keep = ['Ordem', 'Nome', 'Latitude', 'Longitude', 'Coordenadas DMS', 'Endereço', 'Categoria', 'Observações']
        df_mymaps = df_mymaps[[col for col in cols_to_keep if col in df_mymaps.columns]]
        
        return df_mymaps.to_csv(index=False, encoding='utf-8-sig')