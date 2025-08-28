// geoprumo/frontend/src/components/MapView/MapView.jsx

import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, GeoJSON, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// --- Correção para o ícone padrão do marcador ---
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconAnchor: [12, 41] 
});
L.Marker.prototype.options.icon = DefaultIcon;
// --- Fim da correção ---

const FitBounds = ({ route }) => {
  const map = useMap();
  useEffect(() => {
    if (route && route.length > 0) {
      const activePoints = route.filter(p => p.active !== false);
      if (activePoints.length > 0) {
        const bounds = L.latLngBounds(activePoints.map(p => [p.latitude, p.longitude]));
        map.fitBounds(bounds, { padding: [50, 50] });
      }
    }
  }, [route, map]);
  return null;
};

function MapView({ data }) {
  const defaultPosition = [-19.9167, -43.9333];

  const routePoints = data?.optimized_route;
  const routeGeoJson = data?.map_geojson;

  // CORREÇÃO: Adicionamos uma 'key' ao MapContainer.
  // Isso força o mapa a recarregar completamente quando a rota muda, limpando traçados antigos.
  const mapKey = JSON.stringify(routeGeoJson);

  return (
    <MapContainer key={mapKey} center={defaultPosition} zoom={13} style={{ height: '100%', width: '100%', borderRadius: '8px' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />

      {/* Renderiza apenas os marcadores ativos */}
      {routePoints && routePoints.filter(p => p.active !== false).map(point => (
        <Marker key={point.order} position={[point.latitude, point.longitude]}>
          <Popup>
            <b>{point.order}: {point.name}</b><br />
            Lat: {point.latitude.toFixed(5)}, Lon: {point.longitude.toFixed(5)}
          </Popup>
        </Marker>
      ))}

      {routeGeoJson && (
        <GeoJSON data={routeGeoJson} style={{ color: '#007BFF', weight: 5, opacity: 0.8 }} />
      )}
      
      <FitBounds route={routePoints} />
    </MapContainer>
  );
}

export default MapView;