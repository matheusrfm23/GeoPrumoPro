# geoprumo/backend/app/services/ai_services.py (versão corrigida)

import pandas as pd
import google.generativeai as genai
import json
import time
from typing import Dict, Any, List

# --- Importações de módulos do nosso projeto ---
from app.core.config import settings

# --- Constantes ---
BATCH_SIZE = 20 # Processa 20 pontos por vez para otimizar chamadas de API

class AIServices:
    """
    Classe para encapsular todas as interações com a API do Google Gemini.
    """
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("A chave da API do Gemini (GEMINI_API_KEY) não está configurada.")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)

    def _call_gemini_api_with_retries(self, prompt: str, retries: int = 3, delay: int = 5) -> str:
        """
        Função robusta para chamar a API do Gemini, com retentativas em caso de falha.
        """
        for attempt in range(retries):
            try:
                response = self.model.generate_content(prompt)
                
                json_text = response.text.strip()
                if json_text.startswith("```json"):
                    json_text = json_text[7:]
                if json_text.endswith("```"):
                    json_text = json_text[:-3]
                
                return json_text.strip()
            except Exception as e:
                print(f"ERRO na API do Gemini (tentativa {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    raise

    def enrich_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Usa a IA para adicionar informações de endereço e categoria aos pontos, em lotes.
        """
        df_copy = df.copy()
        if 'address' not in df_copy.columns: df_copy['address'] = ""
        if 'category' not in df_copy.columns: df_copy['category'] = ""
        
        # Garante que a coluna 'Nome' exista para evitar erros.
        if 'Nome' not in df_copy.columns:
            df_copy['Nome'] = [f"Ponto {i+1}" for i in range(len(df_copy))]

        for i in range(0, len(df_copy), BATCH_SIZE):
            batch = df_copy.iloc[i:i + BATCH_SIZE]
            points_to_process = []
            for index, row in batch.iterrows():
                # CORREÇÃO: Usa .get() para segurança, embora já garantimos a coluna acima.
                points_to_process.append({
                    "id": index,
                    "nome": row.get('Nome', f"Ponto {index}"),
                    "latitude": row['Latitude'],
                    "longitude": row['Longitude']
                })

            prompt = f"""
            Analise a lista de locais JSON a seguir. Para cada local, forneça o endereço
            completo mais provável e uma categoria (Ex: Serviço Público, Comércio,
            Ponto Turístico, Residencial, Outro).

            Locais:
            {json.dumps(points_to_process, indent=2)}

            Responda APENAS com um array JSON, onde cada objeto contém o "id" original,
            e as chaves "endereco" e "categoria" que você encontrou.
            Exemplo de resposta:
            [
              {{
                "id": 0,
                "endereco": "Praça Sete de Setembro, s/n - Centro, Belo Horizonte - MG, 30130-010, Brasil",
                "categoria": "Ponto Turístico"
              }}
            ]
            """
            try:
                json_text = self._call_gemini_api_with_retries(prompt)
                results = json.loads(json_text)
                
                for result in results:
                    idx = result.get("id")
                    if idx is not None and idx in df_copy.index:
                        df_copy.at[idx, 'address'] = result.get("endereco", "Não encontrado")
                        df_copy.at[idx, 'category'] = result.get("categoria", "Não definida")
            except Exception as e:
                print(f"ERRO ao enriquecer o lote a partir do índice {i}: {e}")
                for index in batch.index:
                    df_copy.at[index, 'address'] = "Erro na busca"
                    df_copy.at[index, 'category'] = "Erro na busca"
        
        return df_copy

    def standardize_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Usa a IA para padronizar os nomes dos locais, em lotes.
        """
        df_copy = df.copy()
        
        # Se a coluna 'Nome' não existir, não há o que fazer. Retorna o DF original.
        if 'Nome' not in df_copy.columns:
            return df_copy

        for i in range(0, len(df_copy), BATCH_SIZE):
            batch = df_copy.iloc[i:i + BATCH_SIZE]
            names_to_process = []
            for index, row in batch.iterrows():
                # CORREÇÃO: Usa .get() para acessar o nome de forma segura.
                nome_original = row.get('Nome', '')
                if nome_original: # Só processa se houver um nome
                    names_to_process.append({"id": index, "nome_original": nome_original})

            if not names_to_process: # Pula o lote se não houver nomes para processar
                continue

            prompt = f"""
            Analise a lista de nomes de locais a seguir. Para cada um, padronize o nome para
            um formato completo e oficial, corrigindo erros de digitação e expandindo
            abreviações (como Av. para Avenida, R. para Rua).

            Nomes:
            {json.dumps(names_to_process, indent=2)}

            Responda APENAS com um array JSON, onde cada objeto contém o "id" original
            e a chave "nome_padronizado".
            Exemplo de resposta:
            [
              {{ "id": 0, "nome_padronizado": "Praça Sete de Setembro" }}
            ]
            """
            try:
                json_text = self._call_gemini_api_with_retries(prompt)
                results = json.loads(json_text)

                for result in results:
                    idx = result.get("id")
                    standardized_name = result.get("nome_padronizado")
                    if idx is not None and standardized_name and idx in df_copy.index:
                        df_copy.at[idx, 'Nome'] = standardized_name
            except Exception as e:
                print(f"ERRO ao padronizar o lote a partir do índice {i}: {e}")
        
        return df_copy