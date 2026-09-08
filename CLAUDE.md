# Job Searcher

## Qué hace
Scraper de Computrabajo.com.ar por keywords, exporta CSV.

## Estructura
- scraper.py: keyword -> lista de ofertas (dict)
- keywords_store.py: maneja historial de keywords (JSON)
- output_writer.py: lista de ofertas -> CSV
- main.py: orquesta el flujo completo

## Cómo correr
python main.py

## Convenciones
- Delay de 1-2 seg entre requests (no saltarse esto)
- Siempre usar User-Agent de navegador real
- Manejar errores de conexión sin crashear todo el script