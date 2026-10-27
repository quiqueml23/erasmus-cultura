# Calendario cultural de Košice

Esta sección genera un feed iCalendar para eventos culturales de Košice, con una alarma siete días antes de cada evento. La web y el feed se publican con GitHub Pages.

- Web: https://quiqueml23.github.io/erasmus-cultura/
- Feed iCalendar: https://quiqueml23.github.io/erasmus-cultura/kosice_cultura.ics
- Datos: [events_data.json](events_data.json)
- Scraper: [scraper.py](scraper.py)
- Generador: [generate_calendar.py](generate_calendar.py)

## Suscripción en iPhone

Abre la web en Safari y usa el botón de suscripción. También puedes pegar la URL del feed en Ajustes → Calendario → Cuentas → Añadir cuenta → Otra → Añadir calendario suscrito.

La frecuencia con que Apple descarga cambios la decide el sistema operativo. La alarma de siete días se incluye en cada evento del feed.

## Datos y actualizaciones

El workflow de GitHub Actions regenera el archivo `.ics` desde `events_data.json` y publica esta carpeta cuando hay cambios o se lanza manualmente. El scraping automático aún necesita selectores fiables y comprobación de fuentes; hasta entonces, los eventos de `events_data.json` son los datos publicados. Verifica fechas, cancelaciones y enlaces en las páginas oficiales antes de confiar en una entrada.

## Ejecución local

Desde la raíz del repositorio:

```bash
python -m pip install -r kosice-cultural-calendar/requirements.txt
python kosice-cultural-calendar/generate_calendar.py
```
