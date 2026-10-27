#!/usr/bin/env python3
"""
Pruebas automatizadas de integridad y conformidad del calendario cultural.
Verifica:
1. Conformidad RFC 5545 del archivo iCalendar generado.
2. Presencia de la alarma a 1 semana (-P7D) en cada evento.
3. Clasificación correcta en español ([Ópera], [Ballet], [Concierto], [Teatro]).
4. Datos obligatorios: recintos, direcciones, enlaces a entradas y fechas válidas.
5. Comportamiento de fusión de datos y estabilidad del scraper.
"""

import os
import unittest
import json
from datetime import timedelta
from icalendar import Calendar
from generate_calendar import generate_ics, build_event, create_base_calendar
from scraper import classify_event, merge_and_save_events


class TestKosiceCalendar(unittest.TestCase):

    def setUp(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.json_path = os.path.join(self.base_dir, "events_data.json")
        self.ics_path = os.path.join(self.base_dir, "kosice_cultura.ics")

    def test_events_json_structure(self):
        """Verifica que events_data.json sea válido y tenga campos requeridos."""
        self.assertTrue(os.path.exists(self.json_path), "events_data.json no existe")
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertGreaterEqual(len(data), 10, "Debe haber al menos 10 eventos confirmados")

        required_keys = ['id', 'title_sk', 'category', 'venue', 'address', 'start', 'ticket_url', 'institution']
        for item in data:
            for k in required_keys:
                self.assertIn(k, item, f"Falta la clave '{k}' en el evento {item.get('id')}")
            self.assertTrue(item['ticket_url'].startswith('http'), f"URL inválida en {item['id']}")

    def test_ics_generation_and_rfc5545(self):
        """Verifica que el archivo .ics generado cumpla las especificaciones requeridas."""
        generate_ics(self.json_path, self.ics_path)
        self.assertTrue(os.path.exists(self.ics_path))

        with open(self.ics_path, 'rb') as f:
            cal = Calendar.from_ical(f.read())

        self.assertEqual(str(cal.get('version')), '2.0')
        self.assertIn('Cultura Košice', str(cal.get('x-wr-calname')))
        self.assertEqual(str(cal.get('x-wr-timezone')), 'Europe/Bratislava')

        subcomponents = list(cal.walk())
        events = [c for c in subcomponents if c.name == 'VEVENT']
        self.assertGreaterEqual(len(events), 10)

        for ev in events:
            summary = str(ev.get('summary'))
            self.assertTrue(summary.startswith('['), f"El resumen debe iniciar con corchetes de categoría: {summary}")
            self.assertIn(']', summary)

            # Verificar presencia de UID y ubicación
            self.assertIsNotNone(ev.get('uid'))
            self.assertIsNotNone(ev.get('location'))
            self.assertIn('Košice', str(ev.get('location')))

            # Verificar la alarma requerida por el usuario: exactamente 1 semana antes (-7 días)
            alarms = [sub for sub in ev.subcomponents if sub.name == 'VALARM']
            self.assertEqual(len(alarms), 1, f"El evento {summary} debe tener exactamente 1 alarma")
            alarm = alarms[0]
            trigger = alarm.get('trigger').dt
            self.assertEqual(trigger, timedelta(days=-7), f"El trigger debe ser de -7 días (1 semana), obtenido: {trigger}")

    def test_category_classification(self):
        """Verifica la lógica de categorización de eventos."""
        self.assertEqual(classify_event("Giuseppe Verdi: La Traviata"), "Ópera")
        self.assertEqual(classify_event("P. I. Tchaikovsky: Luskáčik (Balet)"), "Ballet")
        self.assertEqual(classify_event("Symfonický koncert: A cyklus"), "Concierto")
        self.assertEqual(classify_event("Ján Palárik: Dobrodružstvo pri obžinkoch (Činohra)"), "Teatro")

    def test_merge_stability(self):
        """Verifica que la fusión de eventos no pierda datos existentes."""
        test_db = os.path.join(self.base_dir, "test_events.json")
        try:
            initial = [{
                "id": "test-1",
                "title_sk": "Obra de prueba",
                "category": "Teatro",
                "venue": "Malá scéna",
                "address": "Hlavná 76",
                "start": "2026-12-01T19:00:00",
                "duration_hours": 2.0,
                "description": "Descripción muy detallada de prueba",
                "ticket_url": "https://www.sdke.sk",
                "institution": "Národné divadlo Košice"
            }]
            with open(test_db, 'w', encoding='utf-8') as f:
                json.dump(initial, f)

            new_scraped = [{
                "id": "test-1",
                "title_sk": "Obra de prueba actualizada",
                "category": "Teatro",
                "venue": "Malá scéna",
                "address": "Hlavná 76",
                "start": "2026-12-01T19:00:00",
                "duration_hours": 2.0,
                "description": "corta",
                "ticket_url": "https://www.sdke.sk/test",
                "institution": "Národné divadlo Košice"
            }]

            merged = merge_and_save_events(new_scraped, test_db)
            self.assertEqual(len(merged), 1)
            # Debe mantener la descripción más larga existente
            self.assertEqual(merged[0]['description'], "Descripción muy detallada de prueba")
            self.assertEqual(merged[0]['ticket_url'], "https://www.sdke.sk/test")
        finally:
            if os.path.exists(test_db):
                os.remove(test_db)


if __name__ == "__main__":
    unittest.main()
