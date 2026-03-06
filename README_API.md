# API OpenMeteo (FastAPI)

## Resumo
API em FastAPI que recebe dados de clima no backend e salva em SQLite.

## Estrutura real
- `api/app.py`: cria a aplicacao e registra rotas.
- `api/routes.py`: endpoint de salvamento de clima.
- `api/database.py`: conexao e criacao das tabelas SQLite.
- `api/run.py`: sobe a API e abre o navegador.

## Banco de dados
Arquivo: `api/open_meteo.db`

Tabelas criadas automaticamente:
- `cidade` (`id_cidade`, `nome`, `latitude`, `longitude`)
- `clima_diario` (`id_clima`, `data`, `temperatura`, `umidade`, `vento`, `weathercode`, `id_cidade`)

Observacao: atualmente nao existe regra de unicidade para evitar registros duplicados.

## Como executar
1. Entre na pasta `api`.
2. Instale as dependencias:
   `pip install -r requeriments.txt`
3. Rode a API:
   `python run.py`

Opcional (sem abrir navegador automaticamente):
`uvicorn app:app --reload --port 8000`

## Endpoints
- `GET /` retorna o `index.html`.
- `GET /status` retorna `{"status": "ok"}`.
- `POST /api/v1/weather/salvar-clima` salva os dados enviados no corpo da requisicao.
