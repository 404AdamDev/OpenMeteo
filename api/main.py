from pathlib import Path

from fastapi import FastAPI # type: ignore
from fastapi.responses import FileResponse # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore

from database import init_db
from routes.weather import router as weather_router

app = FastAPI(title="OpenMeteo School API", version="1.0.0")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_FILE = PROJECT_ROOT / "static/index.html"

@app.on_event("startup")
def on_startup() -> None:
    init_db()

app.mount("/js", StaticFiles(directory=PROJECT_ROOT / "static/js"), name="js")
app.mount("/css", StaticFiles(directory=PROJECT_ROOT / "static/css"), name="css")
app.mount("/assets", StaticFiles(directory=PROJECT_ROOT / "static/assets"), name="assets")

@app.get("/")
def home():
    return FileResponse(INDEX_FILE)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

app.include_router(weather_router, prefix="/api")
