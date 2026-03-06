from datetime import datetime
from json import loads
from pathlib import Path
from fastapi import FastAPI
from fastapi import APIRouter, HTTPException, Query
from database import conexaoBD

# Define o roteador para as rotas relacionadas ao clima
router = APIRouter(prefix="/weather", tags=["weather"])

# Função para salvar os dados climáticos no banco de dados
def save_data(data: dict, dias = 7):
    with conexaoBD() as conn:
        # Cria o cursor para executar os comandos SQL no BD
        cursor = conn.cursor()
        cidade = data["cidade"]
        clima_data = data["clima_data"]

        # Salva a cidade no banco de dados
        cursor.execute("INSERT INTO cidade (nome, latitude, longitude) VALUES (?, ?, ?)", (
            cidade, 
            clima_data["latitude"], 
            clima_data["longitude"]
        ))
        id_cidade = cursor.lastrowid

        # Pega os dados climáticos do JSON e salva eles no banco de dados
        hourly = clima_data.get("hourly", {})

        # Extrai os dados climáticos do JSON e salva eles no banco de dados
        datas = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        umids = hourly.get("relative_humidity_2m", [])
        vens = hourly.get("wind_speed_10m", [])
        codes = hourly.get("weather_code", [])

        # Salva os dados climáticos no banco de dados, associando cada registro à cidade correspondente
        for data in range(len(datas) if not dias else min(len(datas), dias * 24)): # Salva os dados climáticos para o número de dias especificado (1-7) ou para todos os dados disponíveis se dias for 0
            cursor.execute("INSERT INTO clima_diario (data, temperatura, umidade, vento, weathercode, id_cidade) VALUES (?, ?, ?, ?, ?, ?)", (
                datas[data],
                temps[data],
                umids[data],
                vens[data],
                codes[data],
                id_cidade
            ))

        conn.commit()

# Rota para salvar os dados climáticos recebidos do frontend, com o número de dias para previsão climática como parâmetro de consulta 
@router.post("/salvar-clima?forecast-days={dias}")
def salvar_clima(data: dict, dias: int = Query(..., description="Número de dias para previsão climática (1-7)")):
    try:
        save_data(data)
    except Exception as exc:
        raise HTTPException( # Retorna um erro 500 caso ocorra algum problema ao salvar os dados climáticos
            status_code=500,
            detail=f"Erro ao salvar dados climáticos: {exc}",
        ) from exc
    
    return {"status": "ok"}