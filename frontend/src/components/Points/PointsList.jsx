// geoprumo/frontend/src/components/Points/PointsList.jsx

import React from 'react';

// Ícones para as ações
const TrashIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
  </svg>
);

function PointsList({ route, onEnrich, isEnriching, onDelete, onToggleActive }) {
  if (!route || route.length === 0) {
    return (
      <div className="flex flex-col h-full">
        <h2 className="text-xl font-bold text-gray-700 mb-2">2. Pontos da Rota</h2>
        <div className="bg-gray-100 p-4 rounded-lg flex items-center justify-center h-full">
          <p className="text-gray-500">Aguardando pontos para exibir a rota...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex justify-between items-center mb-2 flex-shrink-0">
        <h2 className="text-xl font-bold text-gray-700">2. Pontos da Rota</h2>
        <button
          onClick={onEnrich}
          disabled={isEnriching}
          className="bg-purple-600 text-white font-bold py-2 px-3 rounded-lg hover:bg-purple-700 disabled:bg-gray-400 flex items-center text-sm transition-colors"
        >
          {isEnriching ? 'Enriquecendo...' : '✨ Enriquecer com IA'}
        </button>
      </div>

      <div className="overflow-y-auto flex-grow">
        <ul className="space-y-3">
          {route.map((point) => (
            <li
              key={`${point.original_index}-${point.order}`}
              className={`rounded-lg shadow-md border transition-all duration-300 ${point.active === false ? 'bg-gray-100 border-gray-200' : 'bg-white border-white'}`}
            >
              {/* Card Header */}
              <div className={`p-3 border-b border-gray-200 flex justify-between items-start ${point.active === false ? 'opacity-60' : ''}`}>
                <div className="flex items-center gap-3">
                  <span className={`text-white rounded-full h-8 w-8 text-base flex-shrink-0 flex items-center justify-center font-bold transition-colors ${point.active === false ? 'bg-gray-400' : 'bg-blue-600'}`}>
                    {point.order}
                  </span>
                  <p className="font-semibold text-gray-900 break-words">{point.name}</p>
                </div>
                <button onClick={() => onDelete(point.original_index)} className="text-gray-400 hover:text-red-600 transition-colors">
                  <TrashIcon />
                </button>
              </div>

              {/* Card Body */}
              <div className={`p-3 text-sm space-y-2 ${point.active === false ? 'opacity-60' : ''}`}>
                <div className="flex justify-between">
                  <span className="text-gray-500">Coordenadas:</span>
                  <span className="font-mono text-gray-700">
                    {point.latitude.toFixed(5)}, {point.longitude.toFixed(5)}
                  </span>
                </div>
                {point.address && (
                  <div className="flex justify-between items-start gap-2">
                    <span className="text-gray-500 flex-shrink-0">Endereço:</span>
                    <span className="text-right text-gray-700">{point.address}</span>
                  </div>
                )}
                {point.category && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Categoria:</span>
                    <span className="text-right text-gray-700">{point.category}</span>
                  </div>
                )}
              </div>

              {/* Card Footer */}
              <div className="p-3 bg-gray-50 rounded-b-lg flex justify-end items-center">
                <label className="flex items-center cursor-pointer">
                  <span className={`text-sm font-medium mr-3 transition-colors ${point.active === false ? 'text-gray-500' : 'text-gray-700'}`}>
                    {point.active === false ? 'Inativo' : 'Ativo'}
                  </span>
                  <button 
                    onClick={() => onToggleActive(point.original_index)} 
                    className={`relative inline-flex items-center h-6 w-11 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${point.active === false ? 'bg-gray-300' : 'bg-green-500'}`}
                  >
                    <span className={`inline-block w-4 h-4 transform bg-white rounded-full transition-transform ${point.active === false ? 'translate-x-1' : 'translate-x-6'}`} />
                  </button>
                </label>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default PointsList;