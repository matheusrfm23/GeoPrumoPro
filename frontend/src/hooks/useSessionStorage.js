// geoprumo/frontend/src/hooks/useSessionStorage.js

import { useState, useEffect } from 'react';

function useSessionStorage(key, initialValue) {
  // 1. Tenta carregar o valor do localStorage ao iniciar
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error("Erro ao carregar do localStorage:", error);
      return initialValue;
    }
  });

  // 2. Cria um useEffect que salva o valor no localStorage sempre que ele muda
  useEffect(() => {
    try {
      const valueToStore = JSON.stringify(storedValue);
      window.localStorage.setItem(key, valueToStore);
    } catch (error) {
      console.error("Erro ao salvar no localStorage:", error);
    }
  }, [key, storedValue]);

  return [storedValue, setStoredValue];
}

export default useSessionStorage;