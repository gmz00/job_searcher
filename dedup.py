import json
from collections import defaultdict, deque
from difflib import SequenceMatcher
from pathlib import Path

TITULOS_VISTOS_PATH = Path(__file__).parent / "titulos_vistos.json"

# Máximo de registros retenidos en titulos_vistos.json (cola FIFO).
MAX_TITULOS_VISTOS = 2000


def cargar_titulos_vistos() -> deque[dict]:
    """Carga el historial de títulos vistos como una deque de tamaño fijo."""
    if not TITULOS_VISTOS_PATH.exists():
        return deque(maxlen=MAX_TITULOS_VISTOS)

    try:
        with open(TITULOS_VISTOS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"El archivo de titulos_vistos está corrupto o no se pudo leer ({e}), se ignora.")
        return deque(maxlen=MAX_TITULOS_VISTOS)

    if not isinstance(data, list):
        print("El archivo de titulos_vistos tiene un formato inválido, se ignora.")
        return deque(maxlen=MAX_TITULOS_VISTOS)

    # Al construir la deque con maxlen, si data supera MAX_TITULOS_VISTOS
    # se descartarán automáticamente los registros más antiguos (izquierda).
    cola: deque[dict] = deque(maxlen=MAX_TITULOS_VISTOS)
    cola.extend(data)
    return cola


def _agrupar_por_empresa(registros: list[dict] | deque[dict]) -> dict[str, list[dict]]:
    """Devuelve un dict empresa_normalizada -> [registros] para búsqueda O(1)."""
    grupos: dict[str, list[dict]] = defaultdict(list)
    for r in registros:
        empresa = (r.get("empresa") or "").strip().lower()
        if empresa:
            grupos[empresa].append(r)
    return grupos


def _es_similar(titulo_a: str, titulo_b: str, umbral: float = 0.75) -> bool:
    """Compara sólo títulos; la igualdad de empresa ya fue verificada en el llamador."""
    return SequenceMatcher(None, titulo_a, titulo_b).ratio() >= umbral


def filtrar_duplicados(ofertas: list[dict]) -> list[dict]:
    """
    Filtra ofertas duplicadas en dos pasos:
    1. Agrupa por empresa para reducir el espacio de comparación (evita O(n²) global).
    2. Dentro del mismo grupo aplica SequenceMatcher sólo contra ofertas de igual empresa.
    """
    vistos_previos = cargar_titulos_vistos()

    # Índice de títulos previos agrupados por empresa para búsqueda rápida.
    grupos_previos = _agrupar_por_empresa(vistos_previos)

    resultado: list[dict] = []
    # Índice incremental de las ofertas aceptadas en esta pasada.
    grupos_resultado: dict[str, list[dict]] = defaultdict(list)

    for oferta in ofertas:
        titulo = (oferta.get("titulo") or "").strip()
        empresa = (oferta.get("empresa") or "").strip()
        empresa_key = empresa.lower()

        # Sin título o empresa no podemos deduplicar; se acepta directamente.
        if not titulo or not empresa:
            resultado.append(oferta)
            continue

        es_duplicada = False

        # — Paso 1: comparar contra las ofertas ya aceptadas en esta ejecución ——
        for candidato in grupos_resultado[empresa_key]:
            titulo_c = (candidato.get("titulo") or "").strip()
            if _es_similar(titulo, titulo_c):
                es_duplicada = True
                break

        # — Paso 2: comparar contra el historial persistido ————————————————————
        if not es_duplicada:
            for visto in grupos_previos.get(empresa_key, []):
                titulo_v = (visto.get("titulo") or "").strip()
                if _es_similar(titulo, titulo_v):
                    es_duplicada = True
                    break

        if not es_duplicada:
            resultado.append(oferta)
            grupos_resultado[empresa_key].append(oferta)

    return resultado


def guardar_titulos_vistos(ofertas: list[dict]) -> None:
    """
    Persiste los títulos de las ofertas aceptadas. Usa una cola FIFO con
    MAX_TITULOS_VISTOS elementos: los registros más antiguos se descartan
    automáticamente al superar el límite.
    """
    cola = cargar_titulos_vistos()  # ya tiene maxlen=MAX_TITULOS_VISTOS

    for oferta in ofertas:
        titulo = oferta.get("titulo", "")
        empresa = oferta.get("empresa", "")
        if titulo or empresa:
            cola.append({"titulo": titulo, "empresa": empresa})

    with open(TITULOS_VISTOS_PATH, "w", encoding="utf-8") as f:
        json.dump(list(cola), f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    ofertas_prueba = [
        {"id": "1", "titulo": "Desarrollador Python Senior", "empresa": "Acme SA"},
        {"id": "2", "titulo": "Desarrollador Python Sr", "empresa": "Acme SA"},
        {"id": "3", "titulo": "Analista de Sistemas", "empresa": "Beta SRL"},
        {"id": "4", "titulo": "QA Tester", "empresa": "Gamma Corp"},
    ]

    resultado = filtrar_duplicados(ofertas_prueba)
    print(f"Quedaron {len(resultado)} ofertas después del filtro (de {len(ofertas_prueba)} originales)")
    for oferta in resultado:
        print(oferta)
