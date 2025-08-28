// geoprumo/frontend/src/components/ManualAdd/ManualAdd.jsx

import React, { useState, useEffect, useCallback } from 'react';
import { autocompleteAddress } from '../../services/api';

function ManualAdd({ onAddPoint, isLoading }) {
  const [inputValue, setInputValue] = useState('');
  const [suggestions, setSuggestions] = useState([]);

  // Função para buscar sugestões (com debounce)
  const fetchSuggestions = useCallback((query) => {
    autocompleteAddress(query).then(setSuggestions);
  }, []);

  // Efeito para chamar a busca após o usuário parar de digitar
  useEffect(() => {
    if (inputValue.length < 3) {
      setSuggestions([]);
      return;
    }
    // Debounce: espera 300ms antes de chamar a API
    const handler = setTimeout(() => {
      fetchSuggestions(inputValue);
    }, 300);
    // Limpa o timeout se o usuário continuar digitando
    return () => clearTimeout(handler);
  }, [inputValue, fetchSuggestions]);

  const handleAddClick = () => {
    if (inputValue.trim()) {
      onAddPoint(inputValue);
      setInputValue('');
      setSuggestions([]);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInputValue(suggestion);
    setSuggestions([]);
  };

  return (
    <div className="mt-4 relative">
      <label htmlFor="manual-add-input" className="block text-sm font-medium text-gray-700 mb-1">
        Adicionar Ponto por Endereço, CEP ou Coordenadas
      </label>
      <div className="flex space-x-2">
        <input
          type="text"
          id="manual-add-input"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ex: 30130-010 ou Praça Sete, BH"
          className="flex-grow p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          disabled={isLoading}
          autoComplete="off"
        />
        <button
          onClick={handleAddClick}
          disabled={isLoading || !inputValue.trim()}
          className="bg-indigo-600 text-white font-semibold py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {isLoading ? '...' : 'Adicionar'}
        </button>
      </div>
      
      {/* Lista de Sugestões */}
      {suggestions.length > 0 && (
        <ul className="absolute z-10 w-full bg-white border border-gray-300 rounded-md mt-1 shadow-lg max-h-48 overflow-y-auto">
          {suggestions.map((s, i) => (
            <li
              key={i}
              onClick={() => handleSuggestionClick(s)}
              className="p-2 hover:bg-gray-100 cursor-pointer text-sm"
            >
              {s}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default ManualAdd;