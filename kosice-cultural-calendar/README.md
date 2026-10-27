# 🎭 Calendario Cultural de Košice para iPhone
> Ópera, Ballet, Conciertos Sinfónicos y Teatro con avisos automáticos en tu iPhone.

Este proyecto reúne la cartelera cultural de **Košice (Eslovaquia)** y la publica en un formato estándar de suscripción (`.ics` / Webcal) para el calendario de Apple de tu **iPhone, iPad o Mac**, así como para **Google Calendar**.

---

## 🌟 Características Principales

* 🔔 **Avisos automáticos a 1 semana:** Cada evento incluye una alarma programada exactamente **7 días antes**, permitiéndote comprar entradas o reservar la fecha con tiempo.
* 🏛️ **Národné divadlo Košice (NDKE):** Espectáculos de Ópera (*La Traviata*, *Tosca*, *Die Fledermaus*), Ballet (*El Cascanueces*, *Giselle*, *Hamlet*) y Činohra (Teatro).
* 🎻 **Štátna filharmónia Košice (ŠFK):** Ciclos sinfónicos, conciertos de cámara en el Dom umenia y la Kunsthalle, y conciertos extraordinarios de Navidad y Año Nuevo.
* 🏷️ **Etiquetas claras en español:** Cada evento se titula con su categoría identificada: `[Ópera]`, `[Ballet]`, `[Concierto]`, `[Teatro]`.
* 📍 **Recintos y enlaces directos:** Ubicación exacta (con dirección postal para navegación en mapas) y enlace directo a la venta oficial de entradas en la web del teatro o Colosseum.
* 🔄 **Actualización diaria sin coste:** Gracias a GitHub Actions, el calendario busca nuevas funciones cada día a las 06:00 UTC y actualiza tu iPhone sin que tengas que intervenir.

---

## 📱 Cómo suscribirte en tu iPhone

Tienes dos opciones muy sencillas:

### Opción A: Desde tu iPhone en 1 toque (Recomendada)
1. Abre **Safari** en tu iPhone y entra en el enlace de tu repositorio (o página web de GitHub Pages).
2. Toca el botón fucsia **"Añadir al Calendario de mi iPhone"** (o toca directamente el archivo `kosice_cultura.ics`).
3. El iPhone mostrará una ventana emergente:
   > *¿Deseas suscribirte al calendario "Cultura Košice"?*
4. Pulsa **"Suscribirse"** y luego **"Añadir"**.
5. ¡Listo! A partir de ese momento, verás los eventos en tu app Calendario y recibirás la notificación 1 semana antes de cada espectáculo.

### Opción B: Añadirlo manualmente en los Ajustes del iPhone
1. En tu iPhone, entra en **Ajustes** &rarr; **Calendario** &rarr; **Cuentas**.
2. Pulsa en **Añadir cuenta** &rarr; selecciona **Otra** (al final de la lista).
3. Pulsa en **Añadir calendario suscrito**.
4. En el campo *Servidor*, pega el enlace URL de tu calendario: `https://quiqueml23.github.io/erasmus-cultura/kosice_cultura.ics`
5. Pulsa **Siguiente** y luego **Guardar**.

---

## 🌐 ¿Y si prefieres usar Google Calendar?

Si tienes tu cuenta de Google sincronizada con tu iPhone, también puedes añadirlo directamente en Google Calendar y se reflejará solo en tu teléfono:
1. Abre [calendar.google.com](https://calendar.google.com) en tu ordenador o navegador.
2. En la columna izquierda, busca la sección **"Otros calendarios"** y haz clic en el icono **`+`**.
3. Selecciona **"Desde URL"**.
4. Pega la URL: `https://quiqueml23.github.io/erasmus-cultura/kosice_cultura.ics` y pulsa **"Añadir calendario"**.
5. Tu iPhone se sincronizará automáticamente.

---

## 🚀 Cómo sincronizar con tu repositorio `erasmus-cultura`

Tu repositorio está configurado en:
* **Usuario:** `quiqueml23`
* **Repositorio:** [github.com/quiqueml23/erasmus-cultura](https://github.com/quiqueml23/erasmus-cultura)

> 💡 **Nota muy importante sobre la privacidad del repositorio:**
> Para que tu iPhone o Google Calendar puedan leer el calendario sin pedirte contraseñas cada vez, la URL debe ser accesible mediante **GitHub Pages**.
> En las cuentas gratuitas de GitHub, GitHub Pages **únicamente se puede activar en repositorios públicos**.
> Como este repositorio solo contiene la cartelera pública de teatros y conciertos de Košice (sin contraseñas ni datos personales), cambiar la visibilidad de tu repositorio a **Público** (en *Settings* &rarr; *General* &rarr; abajo en *Danger Zone* &rarr; *Change repository visibility*) te permitirá usar GitHub Pages de forma 100% gratuita.

### Cómo subir los archivos:
1. **Mediante la web de GitHub (la forma más fácil y visual):**
   * Entra en [github.com/quiqueml23/erasmus-cultura](https://github.com/quiqueml23/erasmus-cultura).
   * Pulsa en **Add file** &rarr; **Upload files**.
   * Arrastra los archivos de la carpeta local y pulsa en **Commit changes**.

2. **O mediante la terminal:**
   ```bash
   git push -u origin main
   ```
     ```bash
     git init
     git add .
     git commit -m "Versión inicial del calendario cultural"
     git branch -M main
     git remote add origin https://github.com/<tu-usuario>/kosice-cultura.git
     git push -u origin main
     ```

3. **Activar GitHub Pages (Solo una vez):**
   * En tu repositorio de GitHub, entra en **Settings** (Configuración) &rarr; pestaña **Pages**.
   * En la sección **Build and deployment** &rarr; **Source**, selecciona **GitHub Actions**.
   * A partir de ese momento, cada vez que el script se ejecute (o hagas un cambio), se publicará automáticamente en:
     `https://<tu-usuario>.github.io/kosice-cultura/kosice_cultura.ics`
   * Y la versión web interactiva en:
     `https://<tu-usuario>.github.io/kosice-cultura/`

---

## 📁 Estructura del Proyecto

* `kosice_cultura.ics`: Archivo principal de calendario iCalendar (RFC 5545) con todas las funciones y alarmas.
* `events_data.json`: Base de datos de eventos clasificados con títulos, recintos, sinopsis y enlaces.
* `scraper.py`: Script que conecta con `sdke.sk` y `sfk.sk`, procesa la información y mantiene actualizado el calendario.
* `generate_calendar.py`: Módulo que construye el calendario con zonas horarias y alarmas.
* `index.html`: Página web de bienvenida con botón de suscripción en 1 toque y código QR para escanear con la cámara del iPhone.
* `.github/workflows/update-calendar.yml`: Automatización de GitHub Actions que se ejecuta diariamente a las 06:00 UTC.
* `test_calendar.py`: Batería de pruebas automáticas para garantizar que el archivo `.ics` y los avisos funcionen siempre sin fallos.
