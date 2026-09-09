import json
from pathlib import Path

HISTORIAL_PATH = Path("keywords_history.json")


def cargar_historial() -> list[str]:
    if not HISTORIAL_PATH.exists():
        return []

    try:
        with open(HISTORIAL_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"El historial de keywords está corrupto o no se pudo leer ({e}), se ignora.")
        return []

    if not isinstance(data, list):
        print("El historial de keywords tiene un formato inválido, se ignora.")
        return []

    return data


def guardar_historial(keywords: list[str]) -> None:
    historial = cargar_historial()

    existentes_lower = {k.lower() for k in historial}
    combinado = list(historial)
    for keyword in keywords:
        if keyword.lower() not in existentes_lower:
            combinado.append(keyword)
            existentes_lower.add(keyword.lower())

    with open(HISTORIAL_PATH, "w", encoding="utf-8") as f:
        json.dump(combinado, f, indent=2, ensure_ascii=False)


def pedir_keywords() -> list[str]:
    while True:
        historial = cargar_historial()
        seleccionadas = []

        if historial:
            print("Keywords en el historial:")
            for i, keyword in enumerate(historial, start=1):
                print(f"{i}. {keyword}")

            respuesta = input(
                "Ingresá los números de las keywords que querés usar, "
                "separados por coma (Enter para omitir): "
            ).strip()

            if respuesta:
                for parte in respuesta.split(","):
                    parte = parte.strip()
                    if not parte:
                        continue
                    try:
                        numero = int(parte)
                    except ValueError:
                        print(f"Número inválido, se ignora: {parte}")
                        continue
                    if 1 <= numero <= len(historial):
                        seleccionadas.append(historial[numero - 1])
                    else:
                        print(f"Número fuera de rango, se ignora: {numero}")

        respuesta_nuevas = input(
            "Ingresá keywords nuevas separadas por coma (Enter para omitir): "
        ).strip()

        nuevas = [k.strip() for k in respuesta_nuevas.split(",") if k.strip()]

        finales = seleccionadas + nuevas

        if not finales:
            print("Debés ingresar al menos una keyword")
            continue

        if nuevas:
            guardar_historial(nuevas)

        return finales


if __name__ == "__main__":
    resultado = pedir_keywords()
    print("Keywords a usar:", resultado)
