# README

## Endpoint da API usado
- URL base: `https://api.open-meteo.com/v1/forecast`

## Parâmetros utilizados
- `latitude`
- `longitude`
- `hourly`
- `current_weather`
- `timezone`

## Exemplo de resposta (trecho)
```json
{
  "current_weather": {
    "temperature": 22.4,
    "windspeed": 14.8,
    "weathercode": 3
  },
  "hourly": {
    "temperature_2m": [21.9, 22.1, 22.4],
    "windspeed_10m": [12.3, 13.6, 14.8],
    "weathercode": [2, 3, 3]
  }
}
```
