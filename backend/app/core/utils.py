# geoprumo/backend/app/core/utils.py

import math

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    """
    Calcula a distância em metros entre dois pontos geográficos usando a
    fórmula de Haversine.
    """
    R = 6371000  # Raio da Terra em metros
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    a = math.sin(delta_lat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return int(distance)

def decimal_to_dms(deg: float, is_lat: bool) -> str:
    """Converte um grau decimal para uma string em formato DMS."""
    d = int(deg)
    m_float = abs(deg - d) * 60
    m = int(m_float)
    s = (m_float - m) * 60
    
    if is_lat:
        direction = 'N' if deg >= 0 else 'S'
    else:
        direction = 'E' if deg >= 0 else 'W'
        
    # CORREÇÃO: A f-string foi reescrita para ter a sintaxe correta.
    return f"{abs(d)}°{m}'{s:.2f}\" {direction}"