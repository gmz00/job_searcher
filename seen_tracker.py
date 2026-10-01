import json
from collections import deque
from pathlib import Path

SEEN_IDS_PATH = Path(__file__).parent / "seen_ids.json"

# Máximo de IDs retenidos en seen_ids.json (cola FIFO).
# Un ID es un string corto, por lo que 5000 entradas ocupan ~100 KB en disco.
MAX_SEEN_IDS = 5000


def cargar_seen_ids() -> deque[str]:
    """
    Carga los IDs vistos como una deque de tamaño fijo.
    Al superar MAX_SEEN_IDS los IDs más antiguos se descartan automáticamente.
    """
    if not SEEN_IDS_PATH.exists():
        return deque(maxlen=MAX_SEEN_IDS)

    try:
        with open(SEEN_IDS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"El archivo de seen_ids está corrupto o no se pudo leer ({e}), se ignora.")
        return deque(maxlen=MAX_SEEN_IDS)

    if not isinstance(data, list):
        print("El archivo de seen_ids tiene un formato inválido, se ignora.")
        return deque(maxlen=MAX_SEEN_IDS)

    cola: deque[str] = deque(maxlen=MAX_SEEN_IDS)
    cola.extend(str(item) for item in data)
    return cola


def marcar_nuevas(ofertas: list[dict]) -> list[dict]:
    seen_ids = set(cargar_seen_ids())  # set para lookups O(1)

    for oferta in ofertas:
        oferta_id = oferta.get("id")
        oferta["es_nueva"] = oferta_id is None or oferta_id not in seen_ids

    return ofertas


def guardar_seen_ids(ofertas: list[dict]) -> None:
    """
    Persiste los IDs vistos. Aplica límite FIFO: si el total supera
    MAX_SEEN_IDS, los IDs más antiguos son descartados automáticamente.
    """
    cola = cargar_seen_ids()  # ya tiene maxlen=MAX_SEEN_IDS
    ids_actuales = set(cola)  # evita duplicados dentro de la cola

    for oferta in ofertas:
        oferta_id = oferta.get("id")
        if oferta_id is not None and oferta_id not in ids_actuales:
            cola.append(str(oferta_id))
            ids_actuales.add(oferta_id)

    with open(SEEN_IDS_PATH, "w", encoding="utf-8") as f:
        json.dump(list(cola), f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    ofertas_prueba = [
        {"id": "abc123", "titulo": "Desarrollador Python"},
        {"id": "def456", "titulo": "Analista de Sistemas"},
        {"id": "ghi789", "titulo": "QA Tester"},
    ]

    resultado = marcar_nuevas(ofertas_prueba)
    for oferta in resultado:
        print(oferta)

    guardar_seen_ids(resultado)
