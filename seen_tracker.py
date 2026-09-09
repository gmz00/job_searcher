import json
from pathlib import Path

SEEN_IDS_PATH = Path("seen_ids.json")


def cargar_seen_ids() -> set[str]:
    if not SEEN_IDS_PATH.exists():
        return set()

    try:
        with open(SEEN_IDS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"El archivo de seen_ids está corrupto o no se pudo leer ({e}), se ignora.")
        return set()

    if not isinstance(data, list):
        print("El archivo de seen_ids tiene un formato inválido, se ignora.")
        return set()

    return set(data)


def marcar_nuevas(ofertas: list[dict]) -> list[dict]:
    seen_ids = cargar_seen_ids()

    for oferta in ofertas:
        oferta_id = oferta.get("id")
        oferta["es_nueva"] = oferta_id is None or oferta_id not in seen_ids

    return ofertas


def guardar_seen_ids(ofertas: list[dict]) -> None:
    seen_ids = cargar_seen_ids()

    for oferta in ofertas:
        oferta_id = oferta.get("id")
        if oferta_id is not None:
            seen_ids.add(oferta_id)

    with open(SEEN_IDS_PATH, "w", encoding="utf-8") as f:
        json.dump(list(seen_ids), f, indent=2, ensure_ascii=False)


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