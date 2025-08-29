// geoprumo/frontend/src/components/ActionPanel/GoogleMapsLinks.jsx

import React from 'react';

const ExternalLinkIcon = () => (
    <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
    </svg>
);

function GoogleMapsLinks({ links }) {
  if (!links || links.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-lg">
      <h3 className="text-md font-bold text-gray-800 mb-2">Links de Navegação (Google Maps)</h3>
      <p className="text-sm text-gray-600 mb-3">
        Sua rota foi dividida em trechos. O ponto de partida é sempre sua localização atual.
      </p>
      <div className="space-y-2">
        {links.map((link, index) => (
          <a
            key={index}
            href={link}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center w-full bg-blue-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
          >
            {`Abrir Trecho ${index + 1}`}
            <ExternalLinkIcon />
          </a>
        ))}
      </div>
    </div>
  );
}

export default GoogleMapsLinks;
