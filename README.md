# Luke Roberts Home Assistant Integration

Eine Home Assistant Custom Component Integration für Luke Roberts Model F Lampen über die **offizielle Luke Roberts Cloud API** mit vollständiger Unterstützung für:
- Ein/Aus Steuerung
- Helligkeitsregelung
- Farbsteuerung (RGB/HSV)
- Farbtemperatur (Warmweiß bis Kaltweiß)
- Szenen

## Voraussetzungen

- Home Assistant (2023.1 oder neuer)
- Luke Roberts Model F Lampe
- Luke Roberts Cloud Account
- API Token von Luke Roberts
- Lampen-ID (findest du in der Luke Roberts App oder im Web-Interface)

## Installation

### Methode 1: Über VS Code Server Terminal (Empfohlen für HA OS)

Siehe detaillierte Anleitung in [INSTALL.md](INSTALL.md)

```bash
cd /config
git clone https://github.com/zschakDev/luke_roberts_lamp_test.git
cd luke_roberts_lamp_test
chmod +x install_to_homeassistant.sh
./install_to_homeassistant.sh
```

### Methode 2: Manuelle Installation

1. Kopiere den Ordner `custom_components/luke_roberts` in dein Home Assistant `config/custom_components/` Verzeichnis
2. Starte Home Assistant neu

## Konfiguration

### API Token erhalten

1. Melde dich bei [cloud.luke-roberts.com](https://cloud.luke-roberts.com) an
2. Gehe zu deinem Account-Bereich
3. Erstelle einen neuen API Token oder verwende einen bestehenden
4. Kopiere den Token (Format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

### Lampen-ID finden

**Methode 1: Über die Web-App**
1. Öffne [cloud.luke-roberts.com](https://cloud.luke-roberts.com)
2. Klicke auf deine Lampe
3. Die ID steht in der URL: `https://cloud.luke-roberts.com/lamps/1996` → Lampen-ID ist `1996`

**Methode 2: Über die API**
```bash
curl -X GET "https://cloud.luke-roberts.com/api/v1/lamps" \
  -H "Authorization: Bearer DEIN_API_TOKEN"
```

### Integration in Home Assistant einrichten

1. Gehe zu **Einstellungen → Geräte & Dienste**
2. Klicke auf **"+ Integration hinzufügen"**
3. Suche nach **"Luke Roberts"**
4. Gib die folgenden Informationen ein:
   - **API Token**: Dein Luke Roberts Cloud API Token
   - **Lampen-ID**: Die ID deiner Lampe (z.B. `1996`)
   - **Gerätename**: Ein Name für deine Lampe (optional, z.B. "Wohnzimmer Lampe")
5. Klicke auf **"Absenden"**

## Verwendung

Nach der Konfiguration erscheint die Lampe als Light-Entity in Home Assistant.

### Beispiele

```yaml
# Lampe einschalten
service: light.turn_on
target:
  entity_id: light.luke_roberts_lamp_1996

# Helligkeit setzen (0-255)
service: light.turn_on
target:
  entity_id: light.luke_roberts_lamp_1996
data:
  brightness: 200

# Farbtemperatur setzen (2700-4000 Kelvin)
service: light.turn_on
target:
  entity_id: light.luke_roberts_lamp_1996
data:
  color_temp_kelvin: 3000

# Szene auswählen (1-31)
service: light.turn_on
target:
  entity_id: light.luke_roberts_lamp_1996
data:
  effect: "Scene 5"

# Lampe ausschalten
service: light.turn_off
target:
  entity_id: light.luke_roberts_lamp_1996
```

### Verfügbare Funktionen

Gemäß der offiziellen Luke Roberts Cloud API:

- **An/Aus**: Schaltet die Lampe ein oder aus
- **Helligkeit**: Regelung von 0-100%
- **Farbtemperatur**: 2700K (warmweiß) bis 4000K (kaltweiß)
- **Szenen**: Auswahl vordefinierter Szenen (0-31)

### Luke Roberts Model F - Dual-Ring-Architektur

Die Luke Roberts Model F hat **zwei separate Lichtzonen**:

- **Downlight** (unterer Ring): Hauptlicht für direktes weißes Licht nach unten
- **Uplight** (oberer Ring): Akzentlicht für indirektes, farbiges Licht nach oben

Diese Integration verwendet die **Standard-Parameter** `brightness` und `kelvin`, die beide Ringe automatisch korrekt ansteuern. Für normales weißes Licht ist keine manuelle Steuerung der einzelnen Ringe notwendig.

**Wichtig**: Die Cloud API kommuniziert über dein **Smartphone als Bluetooth-Bridge**. Das Handy muss:
- Eingeschaltet sein
- Mit dem Internet verbunden sein
- Die Luke Roberts App installiert haben
- Mit der Lampe gekoppelt sein

Befehle werden über die Cloud an dein Smartphone gesendet, das sie dann per Bluetooth an die Lampe weiterleitet.

**Hinweis**: Für farbige Effekte und spezielle Lichtszenen verwende die integrierten Szenen (Effect-Auswahl).

### Unterstützte Services

- `light.turn_on` - Lampe einschalten (mit optionalen Parametern)
- `light.turn_off` - Lampe ausschalten
- `light.toggle` - Lampe umschalten

## API-Informationen

Diese Integration nutzt die offizielle Luke Roberts Cloud API:

**Base URL**: `https://cloud.luke-roberts.com/api/v1`

**Offizielle Endpunkte**:
- `GET /lamps` - Alle Lampen auflisten
- `PUT /lamps/{id}/command` - Befehle an die Lampe senden

**Authentifizierung**: Bearer Token im Authorization Header

**Wichtig**: Befehle werden asynchron ausgeführt. Die API reiht den Befehl in eine Queue ein, gibt aber keine Rückmeldung, ob die Lampe den Befehl empfangen oder ausgeführt hat.

**Beispiel curl-Befehle**:
```bash
# Lampe einschalten
curl -X PUT "https://cloud.luke-roberts.com/api/v1/lamps/1996/command" \
  -H "Authorization: Bearer DEIN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"power": "ON"}'

# Lampe ausschalten
curl -X PUT "https://cloud.luke-roberts.com/api/v1/lamps/1996/command" \
  -H "Authorization: Bearer DEIN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"power": "OFF"}'

# Helligkeit und Farbtemperatur kombiniert (empfohlen)
curl -X PUT "https://cloud.luke-roberts.com/api/v1/lamps/1996/command" \
  -H "Authorization: Bearer DEIN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"power": "ON", "brightness": 80, "kelvin": 3000}'

# Nur Helligkeit setzen (0-100)
curl -X PUT "https://cloud.luke-roberts.com/api/v1/lamps/1996/command" \
  -H "Authorization: Bearer DEIN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"brightness": 50}'

# Nur Farbtemperatur setzen (2700-4000K)
curl -X PUT "https://cloud.luke-roberts.com/api/v1/lamps/1996/command" \
  -H "Authorization: Bearer DEIN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"kelvin": 3000}'

# Szene auswählen (0-31)
curl -X PUT "https://cloud.luke-roberts.com/api/v1/lamps/1996/command" \
  -H "Authorization: Bearer DEIN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"scene": 5}'
```

## Troubleshooting

### "Invalid API token" Fehler

- Überprüfe, ob dein API Token korrekt ist
- Stelle sicher, dass der Token noch gültig ist
- Erstelle ggf. einen neuen Token in deinem Luke Roberts Account

### "Cannot connect" Fehler

- Überprüfe deine Internetverbindung
- Stelle sicher, dass Home Assistant Zugriff auf das Internet hat
- Prüfe, ob die Luke Roberts Cloud API erreichbar ist

### Lampe reagiert nicht

- Stelle sicher, dass die Lampe mit der Cloud verbunden ist
- Prüfe die Logs in Home Assistant: **Einstellungen → System → Logs**
- Aktiviere Debug-Logging:

```yaml
logger:
  default: info
  logs:
    custom_components.luke_roberts: debug
```

### Falsche Lampen-ID

- Überprüfe die Lampen-ID in der Luke Roberts Web-App
- Verwende den API-Endpunkt `/lamps` um alle verfügbaren Lampen anzuzeigen

## Entwicklung

### Projektstruktur

```
custom_components/luke_roberts/
├── __init__.py          # Integration Setup
├── api.py               # Cloud API Client
├── config_flow.py       # UI-Konfiguration
├── const.py             # Konstanten
├── light.py             # Light Entity
├── manifest.json        # Integration Metadaten
└── translations/
    ├── en.json          # Englisch
    └── de.json          # Deutsch
```

### API Client Features

- Asynchrone HTTP-Requests mit `aiohttp`
- Bearer Token Authentifizierung
- Automatische Fehlerbehandlung
- Timeout-Management
- Debug-Logging

## Mitwirken

Beiträge sind willkommen! Bitte öffne ein Issue oder Pull Request auf GitHub.

## Lizenz

MIT License - siehe [LICENSE](LICENSE)

## Credits

- Basiert auf der offiziellen [Luke Roberts Cloud API](https://cloud.luke-roberts.com/api/v1/documentation)
- Entwickelt für die Luke Roberts Model F Lampe

## Support

Bei Problemen oder Fragen:
1. Prüfe die [Troubleshooting-Sektion](#troubleshooting)
2. Schaue in die Home Assistant Logs
3. Öffne ein [Issue auf GitHub](https://github.com/zschakDev/luke_roberts_lamp_test/issues)

---

**Hinweis**: Diese Integration ist nicht offiziell von Luke Roberts und wird von der Community entwickelt.
