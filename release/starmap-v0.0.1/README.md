# Starmap - Felgenland Saga v0.0.1

A 3D interactive starmap for the **Felgenland Saga** universe, featuring real astronomical data enhanced with fictional political entities, trade networks, and planetary systems.

![Starmap Preview](https://via.placeholder.com/800x400/0c0c0c/00ff88?text=Starmap+Universe+View)

## 🚀 Quick Start

### Windows Users
1. Double-click `start.bat` 
2. Wait for dependencies to install
3. Open http://localhost:8080 in your browser
4. Login with: `admin` / `felgenland_secure_2025`

### Mac/Linux Users
1. Run `./start.sh` in terminal
2. Wait for dependencies to install  
3. Open http://localhost:8080 in your browser
4. Login with: `admin` / `felgenland_secure_2025`

### Manual Installation
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the application
python app.py
```

## 🌌 What's Included

### Universe Data
- **24,676 Real Stars** from Gaia, Hipparcos, and NASA catalogs
- **5 Major Nations** with territories and political systems
- **18 Trade Routes** connecting key systems
- **425+ Exoplanets** including fictional worlds
- **30 Parsec Sphere** around Sol representing human expansion

### Major Political Powers
- **Terran Directorate** (Sol) - Earth-centered authoritarian republic
- **Felgenland Union** (20 LMi) - Trade federation with Eclipse Festival culture  
- **Protelani Republic** (61 UMa) - Ultra-capitalist republic on Protelan moon
- **Dorsai Republic** (Fomalhaut) - Elite military training specialists
- **Pentothian Trade Conglomerate** (Groombridge 1618) - Neutral reptilian traders

## 🎮 How to Use

### Navigation
- **Mouse**: Rotate, zoom, and pan the 3D starmap
- **Click Stars**: View detailed information including planets
- **Search Bar**: Find specific stars or systems
- **Filter Panel**: Adjust magnitude, spectral type, and star count

### Interface Features
- **Nations Toggle**: Show/hide political territories
- **Trade Routes**: Display economic and military connections
- **Galactic Directions**: Show galactic center, poles, and references
- **System Info**: Detailed planetary data for selected stars

### Authentication
- **Web Interface**: Login required for full access
- **API Access**: JWT tokens available for external applications
- **Default Accounts**: `admin` and `starmap_admin` (change in production!)

## 🔧 System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **RAM**: 2GB available memory
- **Storage**: 500MB free space
- **Browser**: Modern browser with WebGL support (Chrome, Firefox, Safari, Edge)

### Recommended
- **Python**: 3.10+
- **RAM**: 4GB+ for better performance
- **GPU**: Dedicated graphics card for smoother 3D rendering
- **Connection**: Stable internet for initial dependency download

## 📁 File Structure

```
starmap-v0.0.1/
├── start.bat              # Windows startup script
├── start.sh               # Mac/Linux startup script  
├── app.py                 # Main application
├── auth.py                # Authentication system
├── requirements.txt       # Python dependencies
├── controllers/           # API controllers
├── models/               # Data models
├── static/               # Web assets (CSS, JS)
├── templates/            # HTML templates
├── data/                 # Universe data files
└── tests/                # Test suite
```

## 🛡️ Security Features

- **Session Authentication**: Secure web interface login
- **JWT Tokens**: API access for external applications
- **Protected Endpoints**: All data modification requires authentication
- **Input Validation**: Prevents malicious data injection
- **CORS Protection**: Secure cross-origin requests

## 🔌 API Access

### Public Endpoints
- `GET /api/stats` - Basic database statistics
- `GET /api/exoplanets` - Real exoplanet data
- `GET /api/stellar-regions` - Galactic regions

### Protected Endpoints (Require Login)
- `GET /api/stars` - Filtered star data
- `GET /api/nations` - Political entities
- `GET /api/search` - Star search functionality
- `POST /api/fictional/*` - Add fictional content

### Generate API Token
```bash
# Login to web interface first, then:
curl -X POST http://localhost:8080/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"expires_hours": 24}'
```

## ⚡ Performance Notes

- **First Launch**: May take 30-60 seconds to initialize database
- **Memory Usage**: ~150MB for full dataset
- **Browser Performance**: Large star counts may impact older devices
- **MontyDB**: Enhanced features enabled automatically if available

## 🔧 Troubleshooting

### Common Issues

**Application won't start**
- Check Python version: `python --version` (need 3.8+)
- Install dependencies: `pip install -r requirements.txt`
- Check port 8080 is available

**Can't access web interface**
- Try http://127.0.0.1:8080 instead of localhost
- Check firewall settings
- Ensure no other applications are using port 8080

**Performance issues**
- Reduce star count limit in filters
- Close other browser tabs
- Enable hardware acceleration in browser

**Login not working**
- Use exact credentials: `admin` / `felgenland_secure_2025`
- Clear browser cache and cookies
- Try incognito/private browsing mode

### Getting Help
- Check log output in terminal for error messages
- Test with different browsers
- Ensure stable internet connection for initial setup

## 📜 License

This project is licensed under the terms specified in the LICENSE file.

## 🌟 Version History

**v0.0.1** - Initial Release
- Complete 3D starmap with 24,676+ stars
- 5 political nations with territories
- Authentication system with web and API access
- Trade route visualization
- Enhanced planetary system data
- Hybrid database architecture (JSON + optional MontyDB)

---

**Explore the Felgenland Saga universe - where political intrigue, trade networks, and frontier conflicts define human expansion among the stars.**