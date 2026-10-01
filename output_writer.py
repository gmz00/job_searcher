import csv
from datetime import date
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"
COLUMNAS = [
    "id",
    "titulo",
    "empresa",
    "ubicacion",
    "modalidad",
    "fecha_publicacion",
    "keyword_busqueda",
    "es_nueva",
    "link",
]


def escribir_csv(ofertas: list[dict]) -> str:
    if not ofertas:
        print("No hay ofertas para guardar")
        return ""

    OUTPUT_DIR.mkdir(exist_ok=True)

    fecha = date.today().isoformat()
    ruta = OUTPUT_DIR / f"{fecha}.csv"

    archivo_nuevo = not ruta.exists()
    modo = "w" if archivo_nuevo else "a"

    with open(ruta, modo, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNAS)
        if archivo_nuevo:
            writer.writeheader()
        for oferta in ofertas:
            fila = {columna: oferta.get(columna, "") for columna in COLUMNAS}
            writer.writerow(fila)

    print(f"Se guardaron {len(ofertas)} ofertas en {ruta}")
    return str(ruta)


if __name__ == "__main__":
    ofertas_prueba = [
        {
            "id": "abc123",
            "titulo": "Desarrollador Python",
            "empresa": "Acme SA",
            "ubicacion": "CABA",
            "modalidad": "Remoto",
            "fecha_publicacion": "2026-09-07",
            "keyword_busqueda": "python",
            "es_nueva": True,
            "link": "https://ar.computrabajo.com/oferta-abc123",
        },
        {
            "id": "def456",
            "titulo": "Analista de Sistemas",
            "empresa": "Beta SRL",
            "ubicacion": "Córdoba",
            "modalidad": "Presencial",
            "fecha_publicacion": "2026-09-06",
            "keyword_busqueda": "analista de sistemas",
            "es_nueva": False,
            "link": "https://ar.computrabajo.com/oferta-def456",
        },
    ]

    escribir_csv(ofertas_prueba)
