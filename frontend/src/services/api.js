// geoprumo/frontend/src/services/api.js

import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

const fileToBase64 = (file) => new Promise((resolve, reject) => {
  const reader = new FileReader();
  reader.readAsDataURL(file);
  reader.onload = () => resolve(reader.result.split(',')[1]);
  reader.onerror = (error) => reject(error);
});

export const optimizeRouteData = async (payload) => {
  const filesAsBase64 = await Promise.all(payload.files.map(async f => ({ filename: f.name, content: await fileToBase64(f) })));
  const requestBody = { files: filesAsBase64, links: payload.links, texts: payload.texts, existing_points: payload.existing_points || [], options: { optimization_mode: 'online' } };
  try {
    const response = await apiClient.post('/process/optimize', requestBody);
    return response.data;
  } catch (error) {
    if (error.response) throw new Error(error.response.data.detail || 'Erro no servidor.');
    if (error.request) throw new Error('Não foi possível se comunicar com o servidor.');
    throw new Error('Erro ao preparar a requisição.');
  }
};

export const enrichRouteWithAI = async (points) => {
  try {
    const response = await apiClient.post('/process/enrich-with-ai', { points });
    return response.data;
  } catch (error) {
    if (error.response) throw new Error(error.response.data.detail || 'Erro no servidor de IA.');
    if (error.request) throw new Error('Não foi possível se comunicar com o servidor de IA.');
    throw new Error('Erro ao preparar a requisição para IA.');
  }
};

export const exportRouteFile = async (format, points) => {
  try {
    const response = await apiClient.post(`/export/${format}`, points, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    const fileExtension = format === 'mymaps' ? 'csv' : format;
    let fileName = `rota_otimizada.${fileExtension}`;
    const contentDisposition = response.headers['content-disposition'];
    if (contentDisposition) {
      const fileNameMatch = contentDisposition.match(/filename="(.+)"/);
      if (fileNameMatch.length === 2) fileName = fileNameMatch[1];
    }
    link.setAttribute('download', fileName);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    console.error(`Erro ao exportar para ${format}:`, error);
    throw new Error(`Não foi possível exportar o arquivo ${format.toUpperCase()}.`);
  }
};

// NOVO: Função para buscar endereço/coordenadas
export const geocodeSearch = async (query) => {
  try {
    // A query é passada como um parâmetro de URL, ex: /search?q=Praça Sete
    const response = await apiClient.get(`/geocode/search`, { params: { q: query } });
    return response.data;
  } catch (error) {
    if (error.response) throw new Error(error.response.data.detail || 'Endereço não encontrado.');
    if (error.request) throw new Error('Não foi possível se comunicar com o servidor.');
    throw new Error('Erro ao preparar a requisição de busca.');
  }
};// NOVA FUNÇÃO DE AUTOCOMPLETE
export const autocompleteAddress = async (query) => {
  if (query.length < 3) return [];
  try {
    const response = await apiClient.get(`/geocode/autocomplete`, { params: { q: query } });
    return response.data;
  } catch (error) {
    console.error("Erro no autocomplete:", error);
    return []; // Retorna vazio em caso de erro
  }
};

export const getGoogleMapsLinks = async (points) => {
  try {
    const response = await apiClient.post('/export/google-maps-links', points);
    return response.data;
  } catch (error) {
    if (error.response) throw new Error(error.response.data.detail || 'Erro ao gerar links do Google Maps.');
    if (error.request) throw new Error('Não foi possível se comunicar com o servidor.');
    throw new Error('Erro ao preparar a requisição para gerar links.');
  }
};