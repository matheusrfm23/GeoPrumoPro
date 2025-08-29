// geoprumo/frontend/src/App.jsx

import React, { useState } from 'react';
import Uploader from './components/Upload/Uploader';
import PointsList from './components/Points/PointsList';
import MapView from './components/MapView/MapView';
import ActionPanel from './components/ActionPanel/ActionPanel';
import ManualAdd from './components/ManualAdd/ManualAdd';
import useSessionStorage from './hooks/useSessionStorage';
import { optimizeRouteData, enrichRouteWithAI, exportRouteFile, geocodeSearch, getGoogleMapsLinks } from './services/api';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [isEnriching, setIsEnriching] = useState(false);
  const [optimizedData, setOptimizedData] = useSessionStorage('geoPrumoSession', null);
  const [error, setError] = useState(null);
  const [pendingData, setPendingData] = useState({ files: [], links: [], texts: [] });
  const [needsReoptimization, setNeedsReoptimization] = useState(false);
  const [googleMapsLinks, setGoogleMapsLinks] = useState([]);

  const handleGenerateMapsLinks = async () => {
    if (!optimizedData || !optimizedData.optimized_route) return;
    setError(null);
    try {
      // Filtra apenas os pontos ativos para enviar para a geração de links
      const activePoints = optimizedData.optimized_route.filter(p => p.active !== false);
      const urls = await getGoogleMapsLinks(activePoints);
      setGoogleMapsLinks(urls);
    } catch (err) {
      setError(err.message);
      setGoogleMapsLinks([]); // Limpa os links em caso de erro
    }
  };

  const handleAddData = (payload) => {
    setPendingData(prevData => ({
      files: [...prevData.files, ...payload.files],
      links: [...prevData.links, ...payload.links],
      texts: [...prevData.texts, ...payload.texts],
    }));
    setNeedsReoptimization(true);
  };
  
  const handleOptimize = async () => {
    const activePoints = optimizedData ? optimizedData.optimized_route.filter(p => p.active !== false) : [];
    const payloadWithExistingPoints = { ...pendingData, existing_points: activePoints };
    if (payloadWithExistingPoints.files.length === 0 && payloadWithExistingPoints.links.length === 0 && payloadWithExistingPoints.texts.length === 0 && payloadWithExistingPoints.existing_points.length === 0) {
      setError("Nenhum ponto para otimizar.");
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const result = await optimizeRouteData(payloadWithExistingPoints);
      const routeWithActiveState = result.optimized_route.map(p => ({ ...p, active: true }));
      setOptimizedData({ ...result, optimized_route: routeWithActiveState });
      setPendingData({ files: [], links: [], texts: [] });
      setNeedsReoptimization(false);
    } catch (err) { setError(err.message); } finally { setIsLoading(false); }
  };

  const handleDeletePoint = (originalIndexToDelete) => {
    setOptimizedData(prevData => ({ ...prevData, optimized_route: prevData.optimized_route.filter(p => p.original_index !== originalIndexToDelete) }));
    setNeedsReoptimization(true);
  };

  const handleTogglePointActive = (originalIndexToToggle) => {
    setOptimizedData(prevData => ({
      ...prevData,
      optimized_route: prevData.optimized_route.map(p => 
        p.original_index === originalIndexToToggle ? { ...p, active: p.active === false ? true : false } : p
      )
    }));
    setNeedsReoptimization(true);
  };

  const handleManualAddPoint = async (query) => {
    setIsLoading(true);
    setError(null);
    try {
      const newPointData = await geocodeSearch(query);
      const newPoint = {
        ...newPointData,
        order: (optimizedData?.optimized_route.length || 0) + 1,
        original_index: `manual-${Date.now()}`,
        active: true,
      };
      setOptimizedData(prevData => ({
        ...prevData,
        optimized_route: [...(prevData?.optimized_route || []), newPoint]
      }));
      setNeedsReoptimization(true);
    } catch (err) { setError(err.message); } finally { setIsLoading(false); }
  };

  const handleEnrich = async () => {
    if (!optimizedData || !optimizedData.optimized_route) return;
    setIsEnriching(true);
    setError(null);
    try {
      const enrichedPoints = await enrichRouteWithAI(optimizedData.optimized_route);
      setOptimizedData(prevData => ({ ...prevData, optimized_route: enrichedPoints }));
    } catch (err) { setError(err.message); } finally { setIsEnriching(false); }
  };
  
  const handleExport = async (format) => {
    if (!optimizedData || !optimizedData.optimized_route) return;
    setError(null);
    try {
      await exportRouteFile(format, optimizedData.optimized_route.filter(p => p.active !== false));
    } catch (err) { setError(err.message); }
  };
  
  const handleReset = () => {
    setOptimizedData(null);
    setPendingData({ files: [], links: [], texts: [] });
    setError(null);
    setNeedsReoptimization(false);
  };
  
  const hasPendingData = pendingData.files.length > 0 || pendingData.links.length > 0 || pendingData.texts.length > 0;
  const hasOptimizedData = optimizedData && optimizedData.optimized_route && optimizedData.optimized_route.length > 0;

  return (
    <div className="bg-gray-100 min-h-screen flex flex-col font-sans">
      <header className="bg-white shadow-md p-4 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center">
            <img src="/GeoPrumo pin.png" alt="Logo GeoPrumo" className="h-10 w-10 mr-4"/>
            <img src="/GeoPrumo completa.jpg" alt="Logotipo Completo GeoPrumo" className="h-10 hidden sm:block"/>
        </div>
        <button onClick={handleReset} className="bg-gray-200 text-gray-700 font-semibold py-2 px-4 rounded-lg hover:bg-gray-300 text-sm">
            Reiniciar Rota
        </button>
      </header>

      <main className="flex-grow container mx-auto p-4 grid grid-cols-1 lg:grid-cols-2 gap-4 lg:h-[calc(100vh-80px)]">
        {/* CORREÇÃO: Layout flexível para a coluna da esquerda */}
        <div className="flex flex-col space-y-4">
          <div className="flex-shrink-0 bg-white p-4 rounded-lg shadow-md">
            <h2 className="text-xl font-bold text-gray-700 mb-2">
              {hasOptimizedData ? 'Gerenciar Pontos' : '1. Adicionar Pontos'}
            </h2>
            <Uploader onProcess={handleAddData} isLoading={isLoading} />
            <ManualAdd onAddPoint={handleManualAddPoint} isLoading={isLoading} />
            {hasPendingData && (
              <div className="mt-4 p-2 bg-yellow-50 border border-yellow-200 rounded">
                <p className="text-sm font-semibold text-yellow-800">Novos dados adicionados. Otimize para atualizar a rota.</p>
              </div>
            )}
            <div className="mt-4 grid grid-cols-1 gap-2">
               <button 
                  onClick={handleOptimize} 
                  disabled={(!hasPendingData && !needsReoptimization) || isLoading} 
                  className="w-full bg-blue-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Otimizando...' : 'Analisar e Otimizar Rota'}
                </button>
            </div>
            {error && <div className="mt-2 text-red-600 font-bold">{error}</div>}
          </div>
          
          <div className="flex-grow bg-white p-4 rounded-lg shadow-md overflow-y-auto min-h-0">
            <PointsList 
              route={optimizedData?.optimized_route} 
              onEnrich={handleEnrich}
              isEnriching={isEnriching}
              onDelete={handleDeletePoint}
              onToggleActive={handleTogglePointActive}
            />
          </div>
          
          {hasOptimizedData && (
            <div className="flex-shrink-0">
              <ActionPanel
                summary={optimizedData.summary}
                onExport={handleExport}
                onGenerateMapsLinks={handleGenerateMapsLinks}
                googleMapsLinks={googleMapsLinks}
              />
            </div>
          )}
        </div>

        <div className="h-96 lg:h-full bg-white p-4 rounded-lg shadow-md">
          <MapView data={optimizedData} />
        </div>
      </main>
    </div>
  );
}

export default App;