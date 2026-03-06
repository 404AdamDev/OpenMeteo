import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "open_meteo.db"

# Define a função de contexto para gerenciar a conexão com o banco de dados
@contextmanager
def conexaoBD() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(DB_PATH)
    
    # Garante que a conexão seja fechada mesmo que ocorra um erro
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

# Define a função para inicializar o banco de dados e criar as tabelas necessárias
def initBD():
    with conexaoBD() as conn:
        cursor = conn.cursor()

        # Cria a tabela cidade 
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cidade (
                id_cidade INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL
            )
        """)

        # Cria a tabela clima_diario com uma chave estrangeira para cidade
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clima_diario (
                id_clima INTEGER PRIMARY KEY AUTOINCREMENT,
                data DATE NOT NULL,
                temperatura REAL NOT NULL,
                umidade REAL NOT NULL,
                vento REAL NOT NULL,
                weathercode INTEGER NOT NULL,
                id_cidade INTEGER NOT NULL,
                FOREIGN KEY(id_cidade) REFERENCES cidade(id_cidade)
            )
        """)