import webbrowser
import threading
import uvicorn
import time

# Abre automaticamente a página de clima no navegador
def abrirNavegador():
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8000")

# Executa o esse arquivo só se ele for solicitado diretamente
if __name__ == "__main__": 
    # Thread para abrir o navegador
    threading.Thread(target=abrirNavegador, daemon=True)
    # Método do uvicorn para criar um app ASVG
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)