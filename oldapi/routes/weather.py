from datetime import datetime
from json import loads
from urllib.parse import urlencode
from urllib.request import urlopen

from fastapi import APIRouter, HTTPException, Query # type: ignore

from database import get_connection

router = APIRouter(prefix="/weather", tags=["weather"])


def fetch_open_meteo(latitude: float, longitude: float, forecast_days: int) -> dict:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m,weather_code",
        "timezone": "auto",
        "forecast_days": forecast_days,
    }
    url = f"https://api.open-meteo.com/v1/forecast?{urlencode(params)}"
    with urlopen(url, timeout=20) as response:
        return loads(response.read().decode("utf-8"))


def aggregate_daily(hourly: dict) -> list[dict]:
    grouped: dict[str, dict[str, list[float | int]]] = {}

    times = hourly.get("time", [])
    temperatures = hourly.get("temperature_2m", [])
    humidities = hourly.get("relative_humidity_2m", [])
    weather_codes = hourly.get("weather_code", [])

    min_size = min(len(times), len(temperatures), len(humidities), len(weather_codes))

    for i in range(min_size):
        timestamp = times[i]
        day = timestamp.split("T")[0]

        if day not in grouped:
            grouped[day] = {"temperature": [], "humidity": [], "weather_codes": []}

        grouped[day]["temperature"].append(temperatures[i])
        grouped[day]["humidity"].append(humidities[i])
        grouped[day]["weather_codes"].append(weather_codes[i])

    rows = []
    for day, values in grouped.items():
        temperature_avg = _average(values["temperature"])
        humidity_avg = _average(values["humidity"])
        weather_mode = _most_common_code(values["weather_codes"])
        rows.append(
            {
                "date": day,
                "temperature": round(temperature_avg, 2),
                "humidity": round(humidity_avg, 2),
                "weather_code": int(weather_mode),
            }
        )

    return sorted(rows, key=lambda row: row["date"])


def _average(numbers: list[float | int]) -> float:
    if not numbers:
        return 0.0
    return float(sum(numbers) / len(numbers))


def _most_common_code(codes: list[float | int]) -> int:
    if not codes:
        return 0

    counts: dict[int, int] = {}
    for code in codes:
        key = int(code)
        counts[key] = counts.get(key, 0) + 1

    return max(counts, key=counts.get)


def _build_records_query(
    city: str | None,
    start_date: str | None,
    end_date: str | None,
) -> tuple[str, list[str]]:
    query = (
        "SELECT id, city, record_date, temperature, humidity, weather_code, created_at "
        "FROM weather_daily WHERE 1=1"
    )
    params: list[str] = []

    if city:
        query += " AND city = ?"
        params.append(city.strip())
    if start_date:
        query += " AND record_date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND record_date <= ?"
        params.append(end_date)

    query += " ORDER BY record_date ASC"
    return query, params


@router.post("/collect")
def collect_weather(
    city: str = Query(..., description="Nome da cidade para armazenar no banco"),
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    forecast_days: int = Query(7, ge=1, le=16),
) -> dict:
    try:
        payload = fetch_open_meteo(
            latitude=latitude,
            longitude=longitude,
            forecast_days=forecast_days,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Erro ao consultar Open-Meteo: {exc}",
        ) from exc

    hourly = payload.get("hourly")
    if not hourly:
        raise HTTPException(
            status_code=502,
            detail="Resposta da Open-Meteo sem bloco 'hourly'",
        )

    daily_rows = aggregate_daily(hourly)
    inserted = 0
    ignored_duplicates = 0

    with get_connection() as conn:
        for row in daily_rows:
            cursor = conn.execute(
                """
                INSERT OR IGNORE INTO weather_daily (city, record_date, temperature, humidity, weather_code)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    city.strip(),
                    row["date"],
                    row["temperature"],
                    row["humidity"],
                    row["weather_code"],
                ),
            )
            if cursor.rowcount == 1:
                inserted += 1
            else:
                ignored_duplicates += 1

    return {
        "city": city,
        "saved_days": len(daily_rows),
        "inserted": inserted,
        "ignored_duplicates": ignored_duplicates,
        "source": "Open-Meteo",
    }


@router.get("/records")
def list_records(
    city: str | None = Query(None, description="Filtrar por cidade"),
    start_date: str | None = Query(None, description="Data inicial YYYY-MM-DD"),
    end_date: str | None = Query(None, description="Data final YYYY-MM-DD"),
) -> dict:
    if start_date:
        _validate_date(start_date, "start_date")
    if end_date:
        _validate_date(end_date, "end_date")

    query, params = _build_records_query(city, start_date, end_date)

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    return {"count": len(rows), "records": [dict(row) for row in rows]}


def _validate_date(value: str, field_name: str) -> None:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} invalida. Use YYYY-MM-DD.",
        ) from exc
