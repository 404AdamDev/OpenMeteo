from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from database import initBD
from routes import router

# Define o caminho para a pasta raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Define o lifespan para inicializar o banco de dados quando a aplicação iniciar
@asynccontextmanager
async def lifespan(app: FastAPI):
    initBD()
    yield

# Cria uma aplicação FastAPI ASVG e inclui as rotas
def criarApp():
    app = FastAPI(title="OpenMeteo API", version="1.0.0", lifespan=lifespan)
    app.include_router(router, prefix="/api/v1") # Define as rotas do routes para serem com "/api/v1/" no inicio

    # Monta os arquivos estáticos para servir o frontend
    app.mount("/static", StaticFiles(directory=PROJECT_ROOT / "static"), name="static") 
    app.mount("/js", StaticFiles(directory=PROJECT_ROOT / "static/js"), name="js")
    app.mount("/css", StaticFiles(directory=PROJECT_ROOT / "static/css"), name="css")
    app.mount("/assets", StaticFiles(directory=PROJECT_ROOT / "static/assets"), name="assets")

    return app
app = criarApp()

# Rota raiz com o arquivo index.html
@app.get("/")
def home():
    return FileResponse(PROJECT_ROOT / "static/index.html")

# Rota para verificar se a API está funcionando
@app.get("/status")
def status():
    return {"status": "ok"}