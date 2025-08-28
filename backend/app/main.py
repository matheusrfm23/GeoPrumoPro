# geoprumo/backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.endpoints import process, export, geocode

app = FastAPI(
    title="GeoPrumo API",
    description="Backend para o otimizador de rotas GeoPrumo.",
    version="1.0.0"
)

# Lista de endereços (origens) que têm permissão para se comunicar com o backend
origins = [
    "http://localhost:3000",
    "http://192.168.0.86:3000", # <-- NOVO ENDEREÇO DE REDE ADICIONADO
    # Adicione aqui outros endereços se necessário (ex: o futuro endereço de produção na Render)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# --- Endpoints (Rotas) ---
app.include_router(process.router)
app.include_router(export.router)
app.include_router(geocode.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"status": "ok", "message": "Bem-vindo à API do GeoPrumo!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)