# Luke Roberts Home Assistant Integration

Eine Home Assistant Custom Component Integration für Luke Roberts Model F Lampen über die **offizielle Luke Roberts Cloud API**.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/release/zschakDev/luke_roberts_lamp_test.svg)](https://github.com/zschakDev/luke_roberts_lamp_test/releases)
[![License](https://img.shields.io/github/license/zschakDev/luke_roberts_lamp_test.svg)](LICENSE)

## ✨ Features

- ✅ **Ein/Aus Steuerung** - Vollständige Power-Kontrolle
- ✅ **Progressive Helligkeitssteuerung** - Optimierte Helligkeitskurve für beste Kontrolle im Alltag
- ✅ **Farbtemperatur** - Warmweiß (2700K) bis Kaltweiß (4000K)
- ✅ **31 Szenen** - Mit individuell anpassbaren Namen
- ✅ **Echtzeit-Synchronisation** - Automatische State-Updates alle 10 Sekunden
- ✅ **Sofortiges Feedback** - UI wird nach Befehlen sofort aktualisiert
- ✅ **Options Flow** - Szenen-Namen einfach über die UI anpassen

### 🎨 Progressive Helligkeitskurve

Die Integration verwendet eine intelligente Helligkeitsskalierung für optimale Kontrolle:

- **0-70% Home Assistant** → 0-50% Lampe (feine Kontrolle im Normalbereich)
- **70-100% Home Assistant** → 50-100% Lampe (Zugang zur vollen Helligkeit)

Dies gibt dir präzise Steuerung wo du sie brauchst, ohne auf maximale Helligkeit verzichten zu müssen.

### 🎭 Individuell benennbare Szenen

Alle 31 Szenen können mit eigenen Namen versehen werden:
- Statt "Scene 5" → "Arbeitslicht"
- Statt "Scene 12" → "Entspannung"
- Statt "Scene 23" → "Romantisch"

## 📦 Installation

### Empfohlen: HACS (Home Assistant Community Store)

1. **HACS öffnen** in Home Assistant
2. **Integrationen** → **3-Punkte-Menü** (oben rechts) → **Benutzerdefinierte Repositories**
3. **Repository hinzufügen:**
   - URL: `https://github.com/zschakDev/luke_roberts_lamp_test`
   - Kategorie: `Integration`
4. **"Luke Roberts"** suchen und **installieren**
5. **Home Assistant neu starten**

### Alternative: Manuelle Installation

<details>
<summary>Klicke hier für manuelle Installationsanleitung</summary>

#### Via VS Code Server Terminal (für Home Assistant OS)

Siehe detaillierte Anleitung in [INSTALL.md](INSTALL.md)

```bash
cd /config
git clone https://github.com/zschakDev/luke_roberts_lamp_test.git
cd luke_roberts_lamp_test
chmod +x install_to_homeassistant.sh
./install_to_homeassistant.sh
```

#### Manuelle Datei-Kopie

1. Lade die [neueste Release](https://github.com/zschakDev/luke_roberts_lamp_test/releases) herunter
2. Kopiere den Ordner `custom_components/luke_roberts` in dein Home Assistant `config/custom_components/` Verzeichnis
3. Starte Home Assistant neu

</details>

## ⚙️ Konfiguration

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

### Szenen-Namen anpassen

1. Gehe zu **Einstellungen → Geräte & Dienste → Luke Roberts**
2. Klicke auf **"Konfigurieren"** bei deiner Lampe
3. Gib für jede der 31 Szenen einen individuellen Namen ein
4. Leere Felder behalten den Standard-Namen "Scene X"
5. **Speichern** - Änderungen werden sofort übernommen (kein Neustart nötig!)

## 🚀 Verwendung

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

# Szene auswählen (mit eigenem Namen)
service: light.turn_on
target:
  entity_id: light.luke_roberts_lamp_1996
data:
  effect: "Arbeitslicht"

# Lampe ausschalten
service: light.turn_off
target:
  entity_id: light.luke_roberts_lamp_1996
```

### Verfügbare Funktionen

Gemäß der offiziellen Luke Roberts Cloud API:

- **An/Aus**: Schaltet die Lampe ein oder aus
- **Helligkeit**: Regelung von 0-100% mit progressiver Kurve
- **Farbtemperatur**: 2700K (warmweiß) bis 4000K (kaltweiß)
- **Szenen**: Auswahl von 31 Szenen mit eigenen Namen

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

## 🔧 API-Informationen

Diese Integration nutzt die offizielle Luke Roberts Cloud API:

**Base URL**: `https://cloud.luke-roberts.com/api/v1`

**Offizielle Endpunkte**:
- `GET /lamps` - Alle Lampen auflisten
- `GET /lamps/{id}/state` - Lampenstatus abrufen
- `PUT /lamps/{id}/command` - Befehle an die Lampe senden

**Authentifizierung**: Bearer Token im Authorization Header

**Wichtig**: Befehle werden asynchron ausgeführt. Die API reiht den Befehl in eine Queue ein, gibt aber keine Rückmeldung, ob die Lampe den Befehl empfangen oder ausgeführt hat.

### ⚠️ Wichtige API-Besonderheiten

**Das Luke Roberts Cloud API funktioniert NUR mit einzelnen Parametern pro Befehl.**

Nach umfangreichen Tests wurde festgestellt:

✅ **Was funktioniert:**
- Einzelne Parameter pro Befehl: `{"power": "ON"}`, `{"brightness": 50}`, `{"kelvin": 3000}`
- Jeder Befehl muss **zweimal gesendet** werden (erstes Mal: Bluetooth-Verbindung aufbauen, zweites Mal: tatsächlicher Befehl)
- 2 Sekunden Delay zwischen den beiden Sends

❌ **Was NICHT funktioniert:**
- Kombinierte Befehle wie `{"power": "ON", "brightness": 50, "kelvin": 3000}`
- Diese führen zu unvorhersehbarem Verhalten (zufällige Szenen, falsche Farben, etc.)

Die Integration berücksichtigt dies automatisch und sendet alle Befehle korrekt nacheinander.

## 🐛 Troubleshooting

### "Invalid API token" Fehler

- Überprüfe, ob dein API Token korrekt ist
- Stelle sicher, dass der Token noch gültig ist
- Erstelle ggf. einen neuen Token in deinem Luke Roberts Account

### "Cannot connect" Fehler

- Überprüfe deine Internetverbindung
- Stelle sicher, dass Home Assistant Zugriff auf das Internet hat
- Prüfe, ob die Luke Roberts Cloud API erreichbar ist

### Lampe reagiert nicht

- **Wichtig**: Dein Smartphone muss eingeschaltet und mit dem Internet verbunden sein (fungiert als Bluetooth-Bridge)
- Stelle sicher, dass die Luke Roberts App auf deinem Smartphone installiert ist
- Überprüfe, ob die Lampe mit deinem Smartphone gekoppelt ist
- Befehle können 4-6 Sekunden dauern (mehrere Commands × 2 Sekunden Delay)
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

### Helligkeit verhält sich seltsam

Die Integration verwendet eine **progressive Helligkeitskurve**:
- 0-70% HA Slider = feine Kontrolle (0-50% Lampe)
- 70-100% HA Slider = Zugang zu voller Helligkeit (50-100% Lampe)

Dies ist beabsichtigt für optimale Kontrolle im Alltag!

## 🔨 Entwicklung

### Projektstruktur

```
custom_components/luke_roberts/
├── __init__.py          # Integration Setup
├── api.py               # Cloud API Client
├── config_flow.py       # UI-Konfiguration & Options Flow
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
- Doppel-Send-Logik für BLE Bridge

### Progressive Brightness Curve

Die Integration implementiert eine zweistufige Helligkeitskurve:

**Segment 1 (0-70% HA → 0-50% API):**
```python
if brightness <= 179:  # 0-70% range
    lamp_brightness = int((brightness / 179) * 50)
```

**Segment 2 (70-100% HA → 50-100% API):**
```python
else:  # 70-100% range
    lamp_brightness = int(50 + ((brightness - 179) / 76) * 50)
```

### State Polling

- Automatisches Polling alle 10 Sekunden
- Sofortige State-Updates nach Befehlen
- Bidirektionale Helligkeitsskalierung

## 🤝 Mitwirken

Beiträge sind willkommen! Bitte öffne ein Issue oder Pull Request auf GitHub.

## 📄 Lizenz

MIT License - siehe [LICENSE](LICENSE)

## 💡 Credits

- Basiert auf der offiziellen [Luke Roberts Cloud API](https://cloud.luke-roberts.com/api/v1/documentation)
- Entwickelt für die Luke Roberts Model F Lampe
- Inspiriert von [denniedegroot/com.luke.roberts](https://github.com/denniedegroot/com.luke.roberts)

## 🆘 Support

Bei Problemen oder Fragen:
1. Prüfe die [Troubleshooting-Sektion](#troubleshooting)
2. Schaue in die Home Assistant Logs
3. Öffne ein [Issue auf GitHub](https://github.com/zschakDev/luke_roberts_lamp_test/issues)

---

**Hinweis**: Diese Integration ist nicht offiziell von Luke Roberts und wird von der Community entwickelt.
