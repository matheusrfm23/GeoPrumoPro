// geoprumo/frontend/src/components/Upload/Uploader.jsx

import React, { useState } from 'react';

function Uploader({ onProcess, isLoading }) {
  const [activeTab, setActiveTab] = useState('files');
  const [currentFiles, setCurrentFiles] = useState([]);
  const [links, setLinks] = useState('');
  const [rawText, setRawText] = useState('');

  const handleFileChange = (event) => {
    const newFiles = Array.from(event.target.files);
    // CORREÇÃO: Adiciona os novos arquivos à lista existente, em vez de substituir.
    setCurrentFiles(prevFiles => [...prevFiles, ...newFiles]);
  };

  const handleSubmit = () => {
    const payload = {
      files: currentFiles,
      links: links.split('\n').filter(link => link.trim() !== ''),
      texts: [rawText].filter(text => text.trim() !== ''),
    };
    onProcess(payload);
    // Limpa os campos para a próxima adição
    setCurrentFiles([]);
    setLinks('');
    setRawText('');
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'files':
        return (
          <div>
            <label htmlFor="file-upload" className="flex justify-center w-full h-32 px-4 transition bg-white border-2 border-gray-300 border-dashed rounded-md appearance-none cursor-pointer hover:border-gray-400 focus:outline-none">
              <span className="flex items-center space-x-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-4-4V6a4 4 0 014-4h1.586a1 1 0 01.707.293l1.414 1.414a1 1 0 00.707.293H12a4 4 0 014 4v1.586a1 1 0 00.293.707l1.414 1.414a1 1 0 01.293.707V16a4 4 0 01-4 4H7z" /></svg>
                <span className="font-medium text-gray-600">Arraste arquivos ou <span className="text-blue-600 underline">procure</span></span>
              </span>
              <input type="file" id="file-upload" name="file-upload" multiple className="hidden" onChange={handleFileChange} />
            </label>
            {currentFiles.length > 0 && (
              <div className="mt-2 text-sm text-gray-500">
                <div className='flex justify-between items-center'>
                  <p className='font-semibold'>Arquivos selecionados:</p>
                  <button onClick={() => setCurrentFiles([])} className='text-xs text-red-500 hover:underline'>Limpar seleção</button>
                </div>
                <ul className='list-disc pl-5 mt-1'>{currentFiles.map((f, i) => <li key={`${f.name}-${i}`}>{f.name}</li>)}</ul>
              </div>
            )}
          </div>
        );
      case 'links':
        return (<textarea className="w-full h-32 p-2 border rounded" placeholder="Cole um ou mais links, um por linha..." value={links} onChange={(e) => setLinks(e.target.value)} />);
      case 'text':
        return (<textarea className="w-full h-32 p-2 border rounded" placeholder="Cole os dados da sua planilha aqui (formato CSV)..." value={rawText} onChange={(e) => setRawText(e.target.value)} />);
      default: return null;
    }
  };

  return (
    <div>
      <div className="border-b border-gray-200 mb-4">
        <nav className="-mb-px flex space-x-4" aria-label="Tabs">
          <button onClick={() => setActiveTab('files')} className={`${activeTab === 'files' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm`}>Arquivos</button>
          <button onClick={() => setActiveTab('links')} className={`${activeTab === 'links' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm`}>Links</button>
          <button onClick={() => setActiveTab('text')} className={`${activeTab === 'text' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm`}>Colar Texto</button>
        </nav>
      </div>
      
      {renderTabContent()}

      <button onClick={handleSubmit} disabled={isLoading || (currentFiles.length === 0 && links.trim() === '' && rawText.trim() === '')} className="mt-4 w-full bg-green-600 text-white font-bold py-2 px-4 rounded hover:bg-green-700 disabled:bg-gray-400 flex items-center justify-center">
        {isLoading ? 'Aguarde...' : 'Adicionar à Lista de Processamento'}
      </button>
    </div>
  );
}

export default Uploader;