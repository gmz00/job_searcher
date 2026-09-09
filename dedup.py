import json
from difflib import SequenceMatcher
from pathlib import Path

TITULOS_VISTOS_PATH = Path("titulos_vistos.json")


def cargar_titulos_vistos() -> list[dict]:
    if not TITULOS_VISTOS_PATH.exists():
        return []

    try:
        with open(TITULOS_VISTOS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"El archivo de titulos_vistos está corrupto o no se pudo leer ({e}), se ignora.")
        return []

    if not isinstance(data, list):
        print("El archivo de titulos_vistos tiene un formato inválido, se ignora.")
        return []

    return data


def _es_similar(titulo_a: str, empresa_a: str, titulo_b: str, empresa_b: str, umbral: float = 0.75) -> bool:
    if empresa_a.strip().lower() != empresa_b.strip().lower():
        return False

    ratio = SequenceMatcher(None, titulo_a, titulo_b).ratio()
    return ratio >= umbral


def filtrar_duplicados(ofertas: list[dict]) -> list[dict]:
    vistos_previos = cargar_titulos_vistos()

    resultado = []
    for oferta in ofertas:
        titulo = oferta.get("titulo") or ""
        empresa = oferta.get("empresa") or ""

        if not titulo or not empresa:
            resultado.append(oferta)
            continue

        es_duplicada = False

        for conservada in resultado:
            titulo_c = conservada.get("titulo") or ""
            empresa_c = conservada.get("empresa") or ""
            if not titulo_c or not empresa_c:
                continue
            if _es_similar(titulo, empresa, titulo_c, empresa_c):
                es_duplicada = True
                break

        if not es_duplicada:
            for visto in vistos_previos:
                titulo_v = visto.get("titulo") or ""
                empresa_v = visto.get("empresa") or ""
                if not titulo_v or not empresa_v:
                    continue
                if _es_similar(titulo, empresa, titulo_v, empresa_v):
                    es_duplicada = True
                    break

        if not es_duplicada:
            resultado.append(oferta)

    return resultado


def guardar_titulos_vistos(ofertas: list[dict]) -> None:
    vistos_previos = cargar_titulos_vistos()

    nuevos = [
        {"titulo": oferta.get("titulo", ""), "empresa": oferta.get("empresa", "")}
        for oferta in ofertas
    ]

    combinado = vistos_previos + nuevos

    with open(TITULOS_VISTOS_PATH, "w", encoding="utf-8") as f:
        json.dump(combinado, f, indent=2, ensure_ascii=False)


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
