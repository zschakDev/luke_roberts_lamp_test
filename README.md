# Luke Roberts Home Assistant Integration

Eine Home Assistant Custom Component Integration für Luke Roberts Model F Lampen mit vollständiger Unterstützung für:
- Ein/Aus Steuerung
- Helligkeitsregelung
- Farbsteuerung (RGB)
- Farbtemperatur (Warmweiß bis Kaltweiß)

## Voraussetzungen

- Home Assistant (2023.1 oder neuer)
- Luke Roberts Model F Lampe
- Ein Gateway/Controller für die Lampe (z.B. basierend auf [LukeRobertsControl](https://github.com/martgras/LukeRobertsControl))
- Die Lampe muss über HTTP API im lokalen Netzwerk erreichbar sein

## Installation

### Methode 1: HACS (Empfohlen)

1. Öffne HACS in Home Assistant
2. Gehe zu "Integrationen"
3. Klicke auf die drei Punkte oben rechts
4. Wähle "Benutzerdefinierte Repositories"
5. Füge diese Repository-URL hinzu: `https://github.com/zschakDev/luke_roberts_lamp_test`
6. Wähle Kategorie "Integration"
7. Suche nach "Luke Roberts" und installiere die Integration
8. Starte Home Assistant neu

### Methode 2: Manuelle Installation

1. Kopiere den Ordner `custom_components/luke_roberts` in dein Home Assistant `config/custom_components/` Verzeichnis
2. Starte Home Assistant neu

## Konfiguration

### Über die UI (Empfohlen)

1. Gehe zu Einstellungen → Geräte & Dienste
2. Klicke auf "+ Integration hinzufügen"
3. Suche nach "Luke Roberts"
4. Gib die folgenden Informationen ein:
   - **IP-Adresse**: Die IP-Adresse deines Luke Roberts Gateways/Controllers
   - **Port**: Der Port des HTTP API (Standard: 80)
   - **Gerätename**: Ein Name für deine Lampe (z.B. "Wohnzimmer Lampe")
5. Klicke auf "Absenden"

### Über configuration.yaml (Legacy)

Diese Integration unterstützt die Konfiguration über die UI (Config Flow). Eine YAML-Konfiguration ist nicht erforderlich.

## Verwendung

Nach der Konfiguration erscheint die Lampe als Light-Entity in Home Assistant:

```yaml
service: light.turn_on
target:
  entity_id: light.wohnzimmer_lampe
data:
  brightness: 255  # 0-255

# Farbtemperatur setzen
service: light.turn_on
target:
  entity_id: light.wohnzimmer_lampe
data:
  color_temp_kelvin: 3000  # 2700-4000 Kelvin

# Farbe setzen
service: light.turn_on
target:
  entity_id: light.wohnzimmer_lampe
data:
  hs_color: [120, 100]  # Hue (0-360), Saturation (0-100)
```

### Verfügbare Funktionen

- **An/Aus**: Schaltet die Lampe ein oder aus
- **Helligkeit**: Regelung von 0-100%
- **Farbtemperatur**: 2700K (warmweiß) bis 4000K (kaltweiß)
- **Farbe**: Vollständige RGB-Farbauswahl über HSV

### Unterstützte Services

- `light.turn_on` - Lampe einschalten (mit optionalen Parametern)
- `light.turn_off` - Lampe ausschalten
- `light.toggle` - Lampe umschalten

## Hardware-Setup

Diese Integration benötigt ein Gateway/Controller-Gerät, das die HTTP API bereitstellt. Empfohlen wird die Verwendung des [LukeRobertsControl](https://github.com/martgras/LukeRobertsControl) Projekts auf einem ESP32.

### API-Endpunkte

Die Integration nutzt folgende HTTP API-Endpunkte:

- `GET http://<ip>:<port>/cm?cmnd=POWER ON/OFF` - Lampe ein/ausschalten
- `GET http://<ip>:<port>/cm?cmnd=DIMMER <0-100>` - Helligkeit setzen
- `GET http://<ip>:<port>/cm?cmnd=KELVIN <2700-4000>` - Farbtemperatur in Kelvin
- `GET http://<ip>:<port>/cm?cmnd=CT <250-416>` - Farbtemperatur in Mireds
- `GET http://<ip>:<port>/cm?cmnd=UPLIGHT <json>` - Uplight-Farbe setzen
- `GET http://<ip>:<port>/cm?cmnd=DOWNLIGHT <json>` - Downlight-Farbe setzen
- `GET http://<ip>:<port>/cm?cmnd=STATE` - Aktuellen Status abrufen

## Troubleshooting

### Verbindung schlägt fehl

- Überprüfe, ob die IP-Adresse korrekt ist
- Stelle sicher, dass der Controller/Gateway eingeschaltet und erreichbar ist
- Prüfe, ob der Port korrekt ist (Standard: 80)
- Teste die Verbindung mit `curl http://<ip>:<port>/cm?cmnd=STATE`

### Lampe reagiert nicht

- Stelle sicher, dass die Lampe mit dem Controller verbunden ist
- Prüfe die Logs in Home Assistant: Einstellungen → System → Logs
- Aktiviere Debug-Logging für detailliertere Informationen:

```yaml
logger:
  default: info
  logs:
    custom_components.luke_roberts: debug
```

### Status wird nicht aktualisiert

Die Integration fragt den Status standardmäßig alle 30 Sekunden ab. Wenn du schnellere Updates brauchst, kannst du das Polling-Intervall anpassen.

## Entwicklung

### Projektstruktur

```
custom_components/luke_roberts/
├── __init__.py          # Integration Setup
├── api.py               # API Client für HTTP-Kommunikation
├── config_flow.py       # UI-Konfiguration
├── const.py             # Konstanten und Konfiguration
├── light.py             # Light Entity Implementation
├── manifest.json        # Integration Metadaten
└── translations/
    ├── en.json          # Englische Übersetzungen
    └── de.json          # Deutsche Übersetzungen
```

### Mitwirken

Beiträge sind willkommen! Bitte öffne ein Issue oder Pull Request auf GitHub.

## Lizenz

MIT License

## Credits

- Basierend auf der [LukeRobertsControl](https://github.com/martgras/LukeRobertsControl) API
- Luke Roberts Official API Documentation

## Support

Bei Problemen oder Fragen:
1. Prüfe die Troubleshooting-Sektion
2. Schaue in die Home Assistant Logs
3. Öffne ein Issue auf GitHub

---

**Hinweis**: Diese Integration ist nicht offiziell von Luke Roberts und wird von der Community entwickelt.