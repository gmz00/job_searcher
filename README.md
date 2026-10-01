# job_searcher

Scraper de ofertas laborales de [Computrabajo Argentina](https://ar.computrabajo.com) por palabras clave. Exporta los resultados a CSV, detecta ofertas nuevas entre ejecuciones y elimina duplicados por similitud de título.

## Características

- Búsqueda por múltiples keywords con historial persistido
- Paginación automática (hasta 50 páginas por keyword)
- Deduplicación fuzzy por título + empresa (SequenceMatcher)
- Marcado de ofertas nuevas vs. ya vistas
- Retry con backoff exponencial ante errores HTTP 429 / 5xx
- Headers HTTP realistas para evitar bloqueos

## Requisitos

- Python 3.12+
- [uv](https://github.com/astral-sh/uv)

## Instalación

```bash
git clone https://github.com/<tu-usuario>/job_searcher.git
cd job_searcher
uv sync
```

## Uso

```bash
uv run main.py
```

Al ejecutarlo se mostrará el historial de keywords anteriores (si existe) y se pedirá ingresar nuevas. Al finalizar se genera un archivo CSV en `output/` con el nombre del día (`YYYY-MM-DD.csv`).

## Estructura del proyecto

```
job_searcher/
├── main.py            # Orquestador principal
├── scraper.py         # Lógica de scraping y parsing HTML
├── dedup.py           # Filtrado de duplicados por similitud
├── seen_tracker.py    # Registro de IDs ya vistos entre ejecuciones
├── keywords_store.py  # Historial de keywords
├── output_writer.py   # Exportación a CSV
└── output/            # CSVs generados (ignorados por git)
```

## Archivos generados en tiempo de ejecución

Los siguientes archivos se crean localmente y están excluidos del repositorio:

| Archivo | Contenido |
|---|---|
| `output/YYYY-MM-DD.csv` | Ofertas del día |
| `seen_ids.json` | IDs de ofertas ya vistas (FIFO, máx. 5000) |
| `titulos_vistos.json` | Títulos para deduplicación (FIFO, máx. 2000) |
| `keywords_history.json` | Historial de keywords ingresadas |

## Dependencias

Gestionadas con `uv` (`pyproject.toml` + `uv.lock`). Para agregar una nueva:

```bash
uv add <paquete>
```
