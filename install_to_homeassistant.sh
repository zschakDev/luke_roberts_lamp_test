#!/bin/bash
# Installations-Script für Luke Roberts Home Assistant Integration

echo "=== Luke Roberts Integration Installer ==="
echo ""

# Home Assistant Config-Verzeichnis (passe dies ggf. an)
HA_CONFIG_DIR="${HA_CONFIG_DIR:-/config}"

# Prüfe ob das HA Config-Verzeichnis existiert
if [ ! -d "$HA_CONFIG_DIR" ]; then
    echo "Fehler: Home Assistant Config-Verzeichnis nicht gefunden: $HA_CONFIG_DIR"
    echo "Bitte setze die Variable HA_CONFIG_DIR auf das richtige Verzeichnis:"
    echo "  export HA_CONFIG_DIR=/dein/pfad/zu/homeassistant/config"
    echo "  ./install_to_homeassistant.sh"
    exit 1
fi

echo "Home Assistant Config-Verzeichnis: $HA_CONFIG_DIR"
echo ""

# Erstelle custom_components Verzeichnis falls nicht vorhanden
mkdir -p "$HA_CONFIG_DIR/custom_components"

# Zielverzeichnis
TARGET_DIR="$HA_CONFIG_DIR/custom_components/luke_roberts"

# Prüfe ob die Integration bereits existiert
if [ -d "$TARGET_DIR" ]; then
    echo "Warnung: Luke Roberts Integration existiert bereits in $TARGET_DIR"
    read -p "Möchtest du sie überschreiben? (j/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[JjYy]$ ]]; then
        echo "Installation abgebrochen."
        exit 0
    fi
    echo "Entferne alte Installation..."
    rm -rf "$TARGET_DIR"
fi

# Kopiere die Integration
echo "Kopiere Luke Roberts Integration nach $TARGET_DIR ..."
cp -r custom_components/luke_roberts "$TARGET_DIR"

# Prüfe ob erfolgreich
if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Installation erfolgreich!"
    echo ""
    echo "Nächste Schritte:"
    echo "1. Starte Home Assistant neu"
    echo "2. Gehe zu Einstellungen → Geräte & Dienste"
    echo "3. Klicke auf '+ Integration hinzufügen'"
    echo "4. Suche nach 'Luke Roberts'"
    echo "5. Konfiguriere deine Lampe"
    echo ""

    # Frage ob HA neu gestartet werden soll
    read -p "Möchtest du Home Assistant jetzt neu starten? (j/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[JjYy]$ ]]; then
        echo "Starte Home Assistant neu..."
        ha core restart 2>/dev/null || echo "Bitte starte Home Assistant manuell neu."
    fi
else
    echo "✗ Fehler beim Kopieren der Dateien!"
    exit 1
fi
