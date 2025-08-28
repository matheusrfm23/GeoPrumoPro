// geoprumo/frontend/public/service-worker.js

const CACHE_NAME = 'geoprumo-cache-v1';
// Lista de arquivos essenciais para a aplicação funcionar offline.
const urlsToCache = [
  '/',
  '/index.html',
  '/manifest.json',
  '/GeoPrumo pin.png',
  '/GeoPrumo completa.jpg',
  // Os arquivos de JS e CSS serão adicionados ao cache dinamicamente.
];

// Evento de Instalação: Salva os arquivos essenciais no cache.
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache aberto');
        return cache.addAll(urlsToCache);
      })
  );
});

// Evento de Fetch: Intercepta os pedidos de rede.
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Se o arquivo existir no cache, serve a partir do cache.
        if (response) {
          return response;
        }

        // Se não, busca na rede, serve para o usuário E salva uma cópia no cache.
        return fetch(event.request).then(
          (response) => {
            // Verifica se recebemos uma resposta válida
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            const responseToCache = response.clone();
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });

            return response;
          }
        );
      })
  );
});

// Evento de Ativação: Limpa caches antigos se uma nova versão for publicada.
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});