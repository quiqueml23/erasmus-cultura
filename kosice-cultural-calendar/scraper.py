#!/usr/bin/env python3
"""
Scraper y sincronizador automático para eventos culturales de Košice.
Fuentes:
  1. Národné divadlo Košice (sdke.sk) - Ópera, Ballet, Činohra (Teatro)
  2. Štátna filharmónia Košice (sfk.sk) - Conciertos sinfónicos y de cámara

Este script se ejecuta automáticamente mediante GitHub Actions (o de forma manual),
extrae los eventos, clasifica cada espectáculo en español ([Ópera], [Ballet], [Concierto], [Teatro]),
conserva y enriquece la base de datos local (events_data.json) y genera el archivo kosice_cultura.ics.
"""

import os
import re
import json
import logging
from datetime import datetime, timedelta
import zoneinfo
import requests
from bs4 import BeautifulSoup
from generate_calendar import generate_ics, TZ_NAME, TZ

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "events_data.json")
ICS_PATH = os.path.join(BASE_DIR, "kosice_cultura.ics")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "sk,en;q=0.8,es;q=0.6"
}


def classify_event(title: str, genre_hint: str = "") -> str:
    """Clasifica el evento en una de las categorías principales en español."""
    text = f"{title} {genre_hint}".lower()

    if any(k in text for k in ["opera", "árie", "puccini", "verdi", "tosca", "traviata", "figaro", "flauta"]):
        return "Ópera"
    if any(k in text for k in ["balet", "luskáčik", "giselle", "labutie", "hamlet", "taneč"]):
        return "Ballet"
    if any(k in text for k in ["koncert", "filharmón", "symfon", "orchestr", "cyklus", "klavír", "husle"]):
        return "Concierto"
    if any(k in text for k in ["činohra", "komédia", "dráma", "divadlo", "havel", "palárik"]):
        return "Teatro"

    return "Cultura"


def scrape_sdke(session: requests.Session) -> list:
    """Extrae eventos del Národné divadlo Košice (sdke.sk)."""
    events = []
    url = "https://www.sdke.sk/"
    try:
        logging.info("Consultando Národné divadlo Košice: %s", url)
        resp = session.get(url, headers=HEADERS, timeout=12)
        if resp.status_code != 200:
            logging.warning("sdke.sk respondió con estado %s", resp.status_code)
            return events

        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Buscar bloques de eventos en el markup de sdke.sk
        event_nodes = soup.find_all(['div', 'article'], class_=re.compile(r'program|event|predstavenie', re.I))
        logging.info("Nodos de eventos potenciales encontrados en sdke.sk: %d", len(event_nodes))

        # El parsing específico de sdke extrae fecha, título, género y recinto
        for node in event_nodes:
            title_tag = node.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'title|nazov', re.I))
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            if len(title) < 3:
                continue

            link_tag = node.find('a', href=True)
            ticket_url = link_tag['href'] if link_tag else url
            if ticket_url.startswith('/'):
                ticket_url = f"https://www.sdke.sk{ticket_url}"

            category = classify_event(title, node.get_text())

            venue = "Historická budova NDKE"
            address = "Hlavná 58, 040 01 Košice"
            if "malá scéna" in node.get_text().lower():
                venue = "Malá scéna NDKE"
                address = "Hlavná 76, 040 01 Košice"

            # Intentar extraer fecha/hora
            date_match = re.search(r'(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})', node.get_text())
            time_match = re.search(r'(\d{1,2}):(\d{2})', node.get_text())

            if date_match and time_match:
                day, month, year = map(int, date_match.groups())
                hour, minute = map(int, time_match.groups())
                dt = datetime(year, month, day, hour, minute)
                slug = re.sub(r'[^a-zA-Z0-9]', '', title.lower())[:15]
                event_id = f"ndke-{year}{month:02d}{day:02d}-{slug}"

                events.append({
                    "id": event_id,
                    "title_sk": title,
                    "category": category,
                    "venue": venue,
                    "address": address,
                    "start": dt.isoformat(),
                    "duration_hours": 2.5 if category in ["Ópera", "Ballet"] else 2.0,
                    "description": f"Función oficial de {category.lower()} en el Národné divadlo Košice.",
                    "ticket_url": ticket_url,
                    "institution": "Národné divadlo Košice"
                })

    except Exception as e:
        logging.warning("No se pudo completar el scraping en directo de sdke.sk: %s", e)

    return events


def scrape_sfk(session: requests.Session) -> list:
    """Extrae eventos de la Štátna filharmónia Košice (sfk.sk)."""
    events = []
    url = "https://www.sfk.sk/kalendar-podujati"
    try:
        logging.info("Consultando Štátna filharmónia Košice: %s", url)
        resp = session.get(url, headers=HEADERS, timeout=12)
        if resp.status_code != 200:
            logging.warning("sfk.sk respondió con estado %s", resp.status_code)
            return events

        soup = BeautifulSoup(resp.text, 'html.parser')
        event_nodes = soup.find_all(['div', 'article'], class_=re.compile(r'event|koncert|podujatie', re.I))
        logging.info("Nodos de conciertos potenciales en sfk.sk: %d", len(event_nodes))

        for node in event_nodes:
            title_tag = node.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'title|nazov', re.I))
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            if len(title) < 3:
                continue

            link_tag = node.find('a', href=True)
            ticket_url = link_tag['href'] if link_tag else url
            if ticket_url.startswith('/'):
                ticket_url = f"https://www.sfk.sk{ticket_url}"

            category = "Concierto"
            venue = "Dom umenia ŠFK"
            address = "Moyzesova 66, 040 01 Košice"
            if "kunsthalle" in node.get_text().lower():
                venue = "Kunsthalle Košice"
                address = "Rumanova 1, 040 01 Košice"

            date_match = re.search(r'(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})', node.get_text())
            time_match = re.search(r'(\d{1,2}):(\d{2})', node.get_text())

            if date_match and time_match:
                day, month, year = map(int, date_match.groups())
                hour, minute = map(int, time_match.groups())
                dt = datetime(year, month, day, hour, minute)
                slug = re.sub(r'[^a-zA-Z0-9]', '', title.lower())[:15]
                event_id = f"sfk-{year}{month:02d}{day:02d}-{slug}"

                events.append({
                    "id": event_id,
                    "title_sk": title,
                    "category": category,
                    "venue": venue,
                    "address": address,
                    "start": dt.isoformat(),
                    "duration_hours": 2.0,
                    "description": f"Concierto sinfónico / de cámara de la Štátna filharmónia Košice.",
                    "ticket_url": ticket_url,
                    "institution": "Štátna filharmónia Košice"
                })

    except Exception as e:
        logging.warning("No se pudo completar el scraping en directo de sfk.sk: %s", e)

    return events


def merge_and_save_events(new_events: list, json_path: str) -> list:
    """Fusiona eventos nuevos con la base de datos existente sin perder información."""
    existing_events = []
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                existing_events = json.load(f)
        except Exception as e:
            logging.error("Error al leer %s: %s", json_path, e)

    events_by_id = {e['id']: e for e in existing_events}

    for ev in new_events:
        # Añadir o actualizar manteniendo datos enriquecidos
        if ev['id'] not in events_by_id:
            events_by_id[ev['id']] = ev
        else:
            # Preservar descripciones más completas si ya existen
            existing = events_by_id[ev['id']]
            if len(existing.get('description', '')) > len(ev.get('description', '')):
                ev['description'] = existing['description']
            events_by_id[ev['id']].update(ev)

    all_events = list(events_by_id.values())
    # Ordenar cronológicamente por fecha de inicio
    all_events.sort(key=lambda x: x.get('start', ''))

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    logging.info("Base de datos de eventos guardada en %s (%d eventos en total)", json_path, len(all_events))
    return all_events


def main():
    logging.info("Iniciando actualización del calendario cultural de Košice...")
    session = requests.Session()

    new_events = []
    # Scraping en vivo
    new_events.extend(scrape_sdke(session))
    new_events.extend(scrape_sfk(session))

    if new_events:
        logging.info("Se extrajeron %d nuevos eventos en vivo.", len(new_events))
    else:
        logging.info("No se extrajeron nuevos eventos en vivo (usando la base existente de eventos confirmados).")

    # Fusionar y actualizar
    all_events = merge_and_save_events(new_events, JSON_PATH)

    # Generar el archivo iCalendar (.ics)
    generate_ics(JSON_PATH, ICS_PATH)
    logging.info("¡Proceso completado exitosamente!")


if __name__ == "__main__":
    main()
