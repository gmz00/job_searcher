from dedup import filtrar_duplicados, guardar_titulos_vistos
from keywords_store import pedir_keywords
from output_writer import escribir_csv
from scraper import scrape_keyword
from seen_tracker import guardar_seen_ids, marcar_nuevas


def main():
    keywords = pedir_keywords()

    ofertas_totales = []
    for keyword in keywords:
        try:
            ofertas = scrape_keyword(keyword)
        except Exception as e:
            print(f"Error scrapeando keyword='{keyword}': {e}")
            continue

        print(f"Se encontraron {len(ofertas)} ofertas para '{keyword}'")
        ofertas_totales.extend(ofertas)

    cantidad_antes_dedup = len(ofertas_totales)
    ofertas_totales = filtrar_duplicados(ofertas_totales)
    descartadas_duplicadas = cantidad_antes_dedup - len(ofertas_totales)
    print(f"Se descartaron {descartadas_duplicadas} ofertas duplicadas")

    if not ofertas_totales:
        print("No se encontraron ofertas para ninguna keyword")
        return

    ofertas_totales = marcar_nuevas(ofertas_totales)
    ruta_csv = escribir_csv(ofertas_totales)
    guardar_seen_ids(ofertas_totales)
    guardar_titulos_vistos(ofertas_totales)

    nuevas = sum(1 for oferta in ofertas_totales if oferta.get("es_nueva"))

    print("\nResumen de la corrida:")
    print(f"Total de ofertas encontradas: {len(ofertas_totales)}")
    print(f"Ofertas nuevas: {nuevas}")
    print(f"Ofertas descartadas por duplicadas: {descartadas_duplicadas}")
    print(f"Keywords buscadas: {', '.join(keywords)}")
    print(f"Archivo CSV generado: {ruta_csv}")


if __name__ == "__main__":
    main()
