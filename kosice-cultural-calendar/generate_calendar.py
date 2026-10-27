#!/usr/bin/env python3
"""
Generador de calendario iCalendar (.ics) para eventos culturales de Košice.
Diseñado para sincronización perfecta con Apple Calendar (iPhone / Mac / iPad)
y Google Calendar.
"""

import json
import os
from datetime import datetime, timedelta
import zoneinfo
from icalendar import Calendar, Event, Alarm, Timezone, TimezoneStandard, TimezoneDaylight

TZ_NAME = "Europe/Bratislava"
TZ = zoneinfo.ZoneInfo(TZ_NAME)


def create_base_calendar() -> Calendar:
    """Crea la estructura base del calendario con metadatos optimizados para Apple Calendar."""
    cal = Calendar()
    cal.add('prodid', '-//Cultura Kosice//Calendario Cultural iPhone//ES')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('x-wr-calname', 'Cultura Košice (Ópera, Ballet, Conciertos)')
    cal.add('x-wr-caldesc', 'Eventos culturales de Košice: Národné divadlo Košice y Štátna filharmónia Košice.')
    cal.add('x-wr-timezone', TZ_NAME)
    cal.add('x-published-ttl', 'P1D')  # Sugerencia de refresco diario para Apple Calendar

    # Componente VTIMEZONE para Europe/Bratislava
    tz_comp = Timezone()
    tz_comp.add('tzid', TZ_NAME)

    # Standard (CET: UTC+1)
    tz_std = TimezoneStandard()
    tz_std.add('tzname', 'CET')
    tz_std.add('dtstart', datetime(1970, 10, 25, 3, 0, 0))
    tz_std.add('rrule', {'freq': 'yearly', 'bymonth': 10, 'byday': '-1su'})
    tz_std.add('tzoffsetfrom', timedelta(hours=2))
    tz_std.add('tzoffsetto', timedelta(hours=1))
    tz_comp.add_component(tz_std)

    # Daylight (CEST: UTC+2)
    tz_dst = TimezoneDaylight()
    tz_dst.add('tzname', 'CEST')
    tz_dst.add('dtstart', datetime(1970, 3, 29, 2, 0, 0))
    tz_dst.add('rrule', {'freq': 'yearly', 'bymonth': 3, 'byday': '-1su'})
    tz_dst.add('tzoffsetfrom', timedelta(hours=1))
    tz_dst.add('tzoffsetto', timedelta(hours=2))
    tz_comp.add_component(tz_dst)

    cal.add_component(tz_comp)
    return cal


def build_event(item: dict) -> Event:
    """Convierte un objeto de evento en un VEVENT compatible con RFC 5545 con alarma a 1 semana."""
    ev = Event()

    # UID único y persistente
    uid = f"{item['id']}@kosice-cultura"
    ev.add('uid', uid)

    # Formato de título con categoría en español: [Ópera] Verdi: La Traviata
    category = item.get('category', 'Cultura')
    title_sk = item.get('title_sk', 'Evento cultural')
    ev.add('summary', f"[{category}] {title_sk}")

    # Fechas de inicio y fin con zona horaria Europe/Bratislava
    start_dt = datetime.fromisoformat(item['start'])
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=TZ)
    duration_hours = item.get('duration_hours', 2.0)
    end_dt = start_dt + timedelta(hours=duration_hours)

    ev.add('dtstart', start_dt)
    ev.add('dtend', end_dt)
    ev.add('dtstamp', datetime.now(zoneinfo.ZoneInfo("UTC")))
    ev.add('created', datetime.now(zoneinfo.ZoneInfo("UTC")))
    ev.add('status', 'CONFIRMED')

    # Ubicación completa con dirección
    venue = item.get('venue', 'Košice')
    address = item.get('address', 'Košice, Eslovaquia')
    full_location = f"{venue}, {address}"
    ev.add('location', full_location)

    # Descripción detallada y pedagógica en español
    description_lines = [
        f"🎭 Tipo de evento: {category}",
        f"🏛️ Institución: {item.get('institution', 'Košice')}",
        f"📍 Recinto: {full_location}",
        "",
        f"ℹ️ Sinopsis / Programa:",
        f"{item.get('description', '')}",
        "",
        f"🎟️ Entradas e información oficial:",
        f"{item.get('ticket_url', 'https://www.sdke.sk')}"
    ]
    ev.add('description', "\n".join(description_lines))

    if 'ticket_url' in item:
        ev.add('url', item['ticket_url'])

    # Alarma requerida por el usuario: exactamente 1 semana antes (-P7D)
    alarm = Alarm()
    alarm.add('action', 'DISPLAY')
    alarm.add('description', f"Aviso (1 semana antes): [{category}] {title_sk}")
    alarm.add('trigger', timedelta(days=-7))
    ev.add_component(alarm)

    return ev


def generate_ics(json_path: str, output_ics_path: str):
    """Genera el archivo .ics a partir del archivo JSON de eventos."""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"No se encontró el archivo: {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        events_data = json.load(f)

    cal = create_base_calendar()

    for item in events_data:
        ev = build_event(item)
        cal.add_component(ev)

    with open(output_ics_path, 'wb') as f:
        f.write(cal.to_ical())

    print(f"Calendario generado con éxito en: {output_ics_path} ({len(events_data)} eventos)")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(base_dir, "events_data.json")
    ics_file = os.path.join(base_dir, "kosice_cultura.ics")
    generate_ics(json_file, ics_file)
