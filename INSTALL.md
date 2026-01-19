# Installation auf Home Assistant via Terminal

## Schnellinstallation (VS Code Server Terminal)

### Schritt 1: Repository klonen
Öffne das Terminal in VS Code Server und führe aus:

```bash
cd /config
git clone https://github.com/zschakDev/luke_roberts_lamp_test.git
cd luke_roberts_lamp_test
```

### Schritt 2: Installation ausführen
```bash
chmod +x install_to_homeassistant.sh
./install_to_homeassistant.sh
```

Das Script wird:
- Die Integration nach `/config/custom_components/luke_roberts/` kopieren
- Dich fragen, ob du Home Assistant neu starten möchtest

### Schritt 3: Home Assistant neu starten
Falls du im Script "nein" gewählt hast, starte manuell neu:
- Gehe zu Einstellungen → System → Neu starten
- Oder über das Terminal: `ha core restart`

### Schritt 4: Integration hinzufügen
Nach dem Neustart:
1. Gehe zu Einstellungen → Geräte & Dienste
2. Klicke auf "+ Integration hinzufügen"
3. Suche nach "Luke Roberts"
4. Gib ein:
   - IP-Adresse deines Luke Roberts Gateways
   - Port (Standard: 80)
   - Gerätename (z.B. "Wohnzimmer Lampe")

---

## Alternative: Manuelle Installation

Falls du das Script nicht verwenden möchtest:

```bash
# Im Home Assistant Terminal
cd /config
git clone https://github.com/zschakDev/luke_roberts_lamp_test.git
mkdir -p /config/custom_components
cp -r luke_roberts_lamp_test/custom_components/luke_roberts /config/custom_components/
ha core restart
```

---

## Deinstallation

```bash
rm -rf /config/custom_components/luke_roberts
ha core restart
```

---

## Troubleshooting

### "git: command not found"
Falls Git nicht installiert ist, kannst du die Dateien auch manuell hochladen:
1. Lade das Repository als ZIP herunter
2. Entpacke es
3. Kopiere den Ordner `custom_components/luke_roberts` nach `/config/custom_components/`

### "ha: command not found"
Verwende die Home Assistant UI zum Neustart:
- Einstellungen → System → Neu starten

### Integration wird nicht gefunden
- Stelle sicher, dass der Ordner korrekt ist: `/config/custom_components/luke_roberts/`
- Prüfe, dass `manifest.json` vorhanden ist
- Lösche den Browser-Cache und lade die Seite neu
- Starte Home Assistant nochmal neu
