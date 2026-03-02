# API Python - OpenMeteo (Projeto Escolar)

## Objetivo
API em FastAPI para:
- consultar a Open-Meteo
- extrair dados de clima por dia
- salvar no SQLite sem duplicar o mesmo dia da mesma cidade

## Estrutura
- `main.py`: inicializa a API
- `database.py`: conexao e inicializacao do SQLite
- `routes/weather.py`: endpoints da atividade
- `sql/create_tables.sql`: script SQL de criacao da tabela

## Modelo Logico
Tabela: `weather_daily`
- `id` (PK)
- `city` (TEXT, NOT NULL)
- `record_date` (DATE, NOT NULL)
- `temperature` (REAL, NOT NULL)
- `humidity` (REAL, NOT NULL)
- `weather_code` (INTEGER, NOT NULL)
- `created_at` (DATETIME, NOT NULL, default CURRENT_TIMESTAMP)
- Restricao: `UNIQUE(city, record_date)`

## DER (texto)
Entidade `weather_daily`
- PK: `id`
- Atributos: `city`, `record_date`, `temperature`, `humidity`, `weather_code`, `created_at`
- Chave candidata/regra de unicidade: `(city, record_date)`

## Duplicidade
Foi usado `INSERT OR IGNORE`, entao se ja existir o mesmo `(city, record_date)` o registro nao e inserido novamente.

## Como rodar
1. Instalar dependencias:
   `pip install -r requirements.txt`
2. Subir API (modo normal):
   `uvicorn main:app --reload --port 8000`
3. Subir API e abrir o `index.html` automaticamente no navegador:
   `python run.py`

## Endpoints
- `GET /health`
- `POST /api/weather/collect?city=Sao%20Paulo&latitude=-23.55&longitude=-46.63&forecast_days=7`
- `GET /api/weather/records`
- `GET /api/weather/records?city=Sao%20Paulo&start_date=2026-03-01&end_date=2026-03-10`
