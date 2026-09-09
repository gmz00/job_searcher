import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://ar.computrabajo.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}
MAX_PAGINAS = 50
DELAY_SEGUNDOS = 1.5


def _keyword_a_url(keyword: str) -> str:
    return keyword.strip().lower().replace(" ", "-")


def _armar_url(keyword_url: str, pagina: int) -> str:
    url = f"{BASE_URL}/trabajo-de-{keyword_url}"
    if pagina > 1:
        url += f"?p={pagina}"
    return url


def _parsear_oferta(article, keyword: str) -> dict:
    oferta = {
        "id": "No especificada",
        "titulo": "No especificada",
        "link": "No especificada",
        "empresa": "No especificada",
        "ubicacion": "No especificada",
        "modalidad": "No especificada",
        "fecha_publicacion": "No especificada",
        "keyword_busqueda": keyword,
    }

    try:
        oferta["id"] = article.get("data-id", "No especificada")
    except Exception as e:
        print(f"Error parseando id de oferta (keyword='{keyword}'): {e}")

    try:
        link_tag = article.find("a", class_="js-o-link")
        if link_tag:
            oferta["titulo"] = link_tag.get_text(strip=True)
            href = link_tag.get("href", "")
            if href.startswith("http"):
                oferta["link"] = href
            elif href:
                oferta["link"] = BASE_URL + href
    except Exception as e:
        print(f"Error parseando titulo/link de oferta (keyword='{keyword}'): {e}")

    try:
        empresa_tag = article.find("a", attrs={"offer-grid-article-company-url": True})
        if empresa_tag:
            oferta["empresa"] = empresa_tag.get_text(strip=True)
    except Exception as e:
        print(f"Error parseando empresa de oferta (keyword='{keyword}'): {e}")

    try:
        ubicacion_tag = article.find("p", class_="fs16 fc_base mt5")
        if ubicacion_tag:
            texto = ubicacion_tag.get_text(strip=True)
            if texto:
                oferta["ubicacion"] = texto
    except Exception as e:
        print(f"Error parseando ubicacion de oferta (keyword='{keyword}'): {e}")

    try:
        icono_remoto = article.find("span", class_="icon i_home")
        if icono_remoto:
            siguiente = icono_remoto.find_next(string=True)
            if siguiente:
                texto = siguiente.strip()
                if texto:
                    oferta["modalidad"] = texto
    except Exception as e:
        print(f"Error parseando modalidad de oferta (keyword='{keyword}'): {e}")

    try:
        fecha_tag = article.find("p", class_="fs13 fc_aux mt15")
        if fecha_tag:
            oferta["fecha_publicacion"] = fecha_tag.get_text(strip=True)
    except Exception as e:
        print(f"Error parseando fecha_publicacion de oferta (keyword='{keyword}'): {e}")

    return oferta


def scrape_keyword(keyword: str) -> list[dict]:
    keyword_url = _keyword_a_url(keyword)
    ofertas = []

    for pagina in range(1, MAX_PAGINAS + 1):
        if pagina > 1:
            time.sleep(DELAY_SEGUNDOS)

        url = _armar_url(keyword_url, pagina)

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error de conexion en pagina {pagina} de keyword='{keyword}': {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("article", class_="box_offer")

        if not articles:
            break

        for article in articles:
            ofertas.append(_parsear_oferta(article, keyword))

    return ofertas


if __name__ == "__main__":
    resultado = scrape_keyword("python")
    print(f"Ofertas encontradas para 'python': {len(resultado)}")
