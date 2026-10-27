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


## Aplicación configurable

La web permite:

- filtrar las categorías visibles (ópera, ballet, teatro, conciertos, cine, zoo, museos, arte, festivales y cultura general);
- marcar individualmente los eventos que se quieren exportar;
- descargar una selección personalizada en formato `.ics`, manteniendo el aviso de siete días;
- consultar un catálogo de fuentes oficiales de Košice y alrededores en [activity_sources.json](activity_sources.json).

Los eventos publicados viven en [events_data.json](events_data.json). El catálogo de fuentes está separado para poder añadir nuevos conectores sin mezclarlo con los eventos ya verificados. Una fuente catalogada no implica que sus eventos se hayan importado todavía: la aplicación muestra el enlace oficial hasta que exista un adaptador de datos fiable.


## Adaptadores de fuentes

El scraper mantiene adaptadores específicos para NDKE y ŠFK y un adaptador genérico para páginas que publican `schema.org/Event` en JSON-LD. Las fuentes con `scrape_mode: "jsonld"` se consultan desde `activity_sources.json`; si una página no expone eventos estructurados, se conserva como fuente enlazada y no se inventan eventos.

Las fuentes pueden definir `feed_url` cuando su agenda está en una ruta distinta de la página pública. Por ejemplo, Kino Úsmev se consulta desde `/program/`, mientras que el enlace mostrado al usuario sigue siendo su portada.

Los adaptadores HTML específicos actuales incluyen Kino Úsmev (películas y horas de cada sesión) y Zoo Košice (actividades con fechas publicadas). Ambos conservan la ficha oficial y dejan el precio como consulta pendiente cuando la fuente no publica una tarifa estructurada.

El catálogo evita fuentes ambiguas: se eliminó la antigua entrada de Kino Družba porque enlazaba a una agenda de Trenčín. Se añadió CINEMAX Košice Optima usando la página oficial de programación y su dirección oficial de Moldavská cesta 32.
