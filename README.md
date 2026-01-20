# Luke Roberts Home Assistant Integration

A Home Assistant Custom Component integration for Luke Roberts Model F lamps using the **official Luke Roberts Cloud API**.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/release/zschakDev/luke_roberts_lamp_test.svg)](https://github.com/zschakDev/luke_roberts_lamp_test/releases)
[![License](https://img.shields.io/github/license/zschakDev/luke_roberts_lamp_test.svg)](LICENSE)

> **⚠️ Disclaimer**: This is a **vibe coding project developed with Claude AI**. The implementation approach and best practices may not be optimal or follow all established conventions. Use at your own risk. Contributions and improvements are welcome!

## ✨ Features

- ✅ **Power Control** - Full on/off control
- ✅ **Progressive Brightness Control** - Optimized brightness curve for better everyday control
- ✅ **Color Temperature** - Warm White (2700K) to Cool White (4000K)
- ✅ **31 Scenes** - With individually customizable names
- ✅ **Real-time Synchronization** - Automatic state updates every 10 seconds
- ✅ **Instant Feedback** - UI updates immediately after commands
- ✅ **Options Flow** - Easy scene name customization via UI

### 🎨 Progressive Brightness Curve

The integration uses intelligent brightness scaling for optimal control:

- **0-70% Home Assistant** → 0-50% Lamp (fine control in normal range)
- **70-100% Home Assistant** → 50-100% Lamp (access to full brightness)

This gives you precise control where you need it, without sacrificing access to maximum brightness.

### 🎭 Customizable Scene Names

All 31 scenes can be renamed:
- Instead of "Scene 5" → "Work Light"
- Instead of "Scene 12" → "Relaxation"
- Instead of "Scene 23" → "Romantic"

## 📦 Installation

### Recommended: HACS (Home Assistant Community Store)

1. **Open HACS** in Home Assistant
2. **Integrations** → **3-dot menu** (top right) → **Custom repositories**
3. **Add Repository:**
   - URL: `https://github.com/zschakDev/luke_roberts_lamp_test`
   - Category: `Integration`
4. **Search for "Luke Roberts"** and **install**
5. **Restart Home Assistant**

### Alternative: Manual Installation

<details>
<summary>Click here for manual installation instructions</summary>

#### Via VS Code Server Terminal (for Home Assistant OS)

See detailed instructions in [INSTALL.md](INSTALL.md)

```bash
cd /config
git clone https://github.com/zschakDev/luke_roberts_lamp_test.git
cd luke_roberts_lamp_test
chmod +x install_to_homeassistant.sh
./install_to_homeassistant.sh
```

#### Manual File Copy

1. Download the [latest release](https://github.com/zschakDev/luke_roberts_lamp_test/releases)
2. Copy the `custom_components/luke_roberts` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

</details>

## ⚙️ Configuration

### Get API Token

1. Log in to [cloud.luke-roberts.com](https://cloud.luke-roberts.com)
2. Go to your account area
3. Create a new API token or use an existing one
4. Copy the token (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

### Find Lamp ID

**Method 1: Via Web App**
1. Open [cloud.luke-roberts.com](https://cloud.luke-roberts.com)
2. Click on your lamp
3. The ID is in the URL: `https://cloud.luke-roberts.com/lamps/XXXX` → Lamp ID is `XXXX`

**Method 2: Via API**
```bash
curl -X GET "https://cloud.luke-roberts.com/api/v1/lamps" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

### Set Up Integration in Home Assistant

1. Go to **Settings → Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"Luke Roberts"**
4. Enter the following information:
   - **API Token**: Your Luke Roberts Cloud API token
   - **Lamp ID**: Your lamp's ID (e.g., `1996`)
   - **Device Name**: A name for your lamp (optional, e.g., "Living Room Lamp")
5. Click **"Submit"**

### Customize Scene Names

1. Go to **Settings → Devices & Services → Luke Roberts**
2. Click **"Configure"** on your lamp
3. Enter individual names for each of the 31 scenes
4. Empty fields keep the default name "Scene X"
5. **Save** - Changes apply immediately (no restart needed!)

## 🚀 Usage

After configuration, the lamp appears as a Light entity in Home Assistant.

### Examples

```yaml
# Turn on lamp
service: light.turn_on
target:
  entity_id: light.luke_roberts_lamp_1996

# Set brightness (0-255)
service: light.turn_on
target:
  entity_id: light.luke_roberts_lamp_1996
data:
  brightness: 200

# Set color temperature (2700-4000 Kelvin)
service: light.turn_on
target:
  entity_id: light.luke_roberts_lamp_1996
data:
  color_temp_kelvin: 3000

# Select scene (with custom name)
service: light.turn_on
target:
  entity_id: light.luke_roberts_lamp_1996
data:
  effect: "Work Light"

# Turn off lamp
service: light.turn_off
target:
  entity_id: light.luke_roberts_lamp_1996
```

### Available Functions

According to the official Luke Roberts Cloud API:

- **Power**: Turn the lamp on or off
- **Brightness**: Control from 0-100% with progressive curve
- **Color Temperature**: 2700K (warm white) to 4000K (cool white)
- **Scenes**: Selection of 31 scenes with custom names

### Luke Roberts Model F - Dual-Ring Architecture

The Luke Roberts Model F has **two separate light zones**:

- **Downlight** (bottom ring): Main light for direct white light downward
- **Uplight** (top ring): Accent light for indirect, colored light upward

This integration uses the **standard parameters** `brightness` and `kelvin`, which automatically control both rings correctly. Manual control of individual rings is not necessary for normal white light.

**Important**: The Cloud API communicates via your **smartphone as a Bluetooth bridge**. Your phone must be:
- Turned on
- Connected to the internet
- Have the Luke Roberts app installed
- Paired with the lamp

Commands are sent via the cloud to your smartphone, which then forwards them via Bluetooth to the lamp.

**Note**: For colored effects and special light scenes, use the integrated scenes (Effect selection).

## 🔧 API Information

This integration uses the official Luke Roberts Cloud API:

**Base URL**: `https://cloud.luke-roberts.com/api/v1`

**Official Endpoints**:
- `GET /lamps` - List all lamps
- `GET /lamps/{id}/state` - Get lamp status
- `PUT /lamps/{id}/command` - Send commands to lamp

**Authentication**: Bearer Token in Authorization Header

**Important**: Commands are executed asynchronously. The API queues the command but does not indicate whether the lamp has received or executed it.

### ⚠️ Important API Quirks

**The Luke Roberts Cloud API ONLY works with single parameters per command.**

After extensive testing, we found:

✅ **What works:**
- Single parameters per command: `{"power": "ON"}`, `{"brightness": 50}`, `{"kelvin": 3000}`
- Each command must be sent **twice** (first time: establish Bluetooth connection, second time: actual command)
- 2 second delay between the two sends

❌ **What DOESN'T work:**
- Combined commands like `{"power": "ON", "brightness": 50, "kelvin": 3000}`
- These lead to unpredictable behavior (random scenes, wrong colors, etc.)

The integration handles this automatically and sends all commands correctly in sequence.

## 🐛 Troubleshooting

### "Invalid API token" Error

- Check if your API token is correct
- Ensure the token is still valid
- Create a new token in your Luke Roberts account if needed

### "Cannot connect" Error

- Check your internet connection
- Ensure Home Assistant has internet access
- Check if the Luke Roberts Cloud API is reachable

### Lamp Not Responding

- **Important**: Your smartphone must be on and connected to the internet (acts as Bluetooth bridge)
- Ensure the Luke Roberts app is installed on your smartphone
- Check if the lamp is paired with your smartphone
- Commands can take 4-6 seconds (multiple commands × 2 seconds delay)
- Check logs in Home Assistant: **Settings → System → Logs**
- Enable debug logging:

```yaml
logger:
  default: info
  logs:
    custom_components.luke_roberts: debug
```

### Wrong Lamp ID

- Check the lamp ID in the Luke Roberts web app
- Use the `/lamps` API endpoint to list all available lamps

### Brightness Behaves Strangely

The integration uses a **progressive brightness curve**:
- 0-70% HA slider = fine control (0-50% lamp)
- 70-100% HA slider = access to full brightness (50-100% lamp)

This is intentional for optimal everyday control!

## 🔨 Development

### Project Structure

```
custom_components/luke_roberts/
├── __init__.py          # Integration Setup
├── api.py               # Cloud API Client
├── config_flow.py       # UI Configuration & Options Flow
├── const.py             # Constants
├── light.py             # Light Entity
├── manifest.json        # Integration Metadata
└── translations/
    ├── en.json          # English
    └── de.json          # German
```

### API Client Features

- Asynchronous HTTP requests with `aiohttp`
- Bearer Token authentication
- Automatic error handling
- Timeout management
- Debug logging
- Double-send logic for BLE bridge

### Progressive Brightness Curve

The integration implements a two-segment brightness curve:

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

- Automatic polling every 10 seconds
- Immediate state updates after commands
- Bidirectional brightness scaling

## 🤝 Contributing

Contributions are welcome! Please open an issue or pull request on GitHub.

Since this is a vibe coding project with Claude AI, there may be areas for improvement in terms of:
- Code architecture and patterns
- Home Assistant best practices
- Error handling
- Performance optimization
- Documentation

Feel free to suggest improvements or submit PRs!

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 💡 Credits

- Based on the official [Luke Roberts Cloud API](https://cloud.luke-roberts.com/api/v1/documentation)
- Developed for the Luke Roberts Model F lamp
- Inspired by [denniedegroot/com.luke.roberts](https://github.com/denniedegroot/com.luke.roberts)
- **Vibe coded with Claude AI** - an experiment in AI-assisted development

## 🆘 Support

For issues or questions:
1. Check the [Troubleshooting section](#troubleshooting)
2. Review the Home Assistant logs
3. Open an [issue on GitHub](https://github.com/zschakDev/luke_roberts_lamp_test/issues)

---

**Note**: This integration is not official from Luke Roberts and is community-developed. This is a vibe coding project created with AI assistance - use at your own discretion.
