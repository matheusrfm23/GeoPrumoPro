// geoprumo/frontend/src/components/ActionPanel/ActionPanel.jsx (versão final)

import React from 'react';
import GoogleMapsLinks from './GoogleMapsLinks';

const DownloadIcon = () => (
  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
  </svg>
);

function ActionPanel({ summary, onExport, onGenerateMapsLinks, googleMapsLinks }) {
  if (!summary) return null;

  const exportFormats = ['csv', 'kml', 'gpx', 'geojson'];

  return (
    <div className="bg-white p-4 rounded-lg shadow-md">
      <h2 className="text-xl font-bold text-gray-700 mb-3">3. Resultados e Exportação</h2>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-blue-50 p-3 rounded-lg text-center">
          <p className="text-sm text-blue-800 font-semibold">Distância Total</p>
          <p className="text-2xl font-bold text-blue-900">{summary.distance_km.toFixed(1)} km</p>
        </div>
        <div className="bg-green-50 p-3 rounded-lg text-center">
          <p className="text-sm text-green-800 font-semibold">Duração Estimada</p>
          <p className="text-2xl font-bold text-green-900">{summary.duration_min.toFixed(0)} min</p>
        </div>
      </div>
      
      {/* Botão para Gerar Links do Google Maps */}
      <button
        onClick={onGenerateMapsLinks}
        className="w-full bg-blue-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-700 flex items-center justify-center transition-colors mb-4 text-base"
      >
        Gerar Links de Navegação (Google Maps)
      </button>

      {/* Componente que exibe os links gerados */}
      <GoogleMapsLinks links={googleMapsLinks} />
      
      <div className="border-t my-4"></div>

      {/* Botão de Destaque para My Maps */}
      <button
        onClick={() => onExport('mymaps')}
        className="w-full bg-green-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-green-700 flex items-center justify-center transition-colors mb-2"
      >
        <DownloadIcon />
        Exportar para My Maps (CSV)
      </button>

      {/* Outros Botões de Exportação */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {exportFormats.map(format => (
          <button
            key={format}
            onClick={() => onExport(format)}
            className="bg-gray-700 text-white text-sm font-semibold py-2 px-3 rounded-md hover:bg-gray-800 flex items-center justify-center transition-colors"
          >
            <DownloadIcon />
            {format.toUpperCase()}
          </button>
        ))}
      </div>
    </div>
  );
}

export default ActionPanel; 