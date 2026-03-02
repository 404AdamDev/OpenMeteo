CREATE TABLE IF NOT EXISTS weather_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    record_date DATE NOT NULL,
    temperature REAL NOT NULL,
    humidity REAL NOT NULL,
    weather_code INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (city, record_date)
);
