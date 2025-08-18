# Starmap - Felgenland Saga Installation Guide

Complete installation instructions for all platforms.

## 📦 Download

**Latest Release**: [starmap-felgenland-saga-v0.0.1.zip](starmap-felgenland-saga-v0.0.1.zip) (42MB)

## 🖥️ System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **RAM**: 2GB available memory  
- **Storage**: 500MB free space
- **Internet**: For initial dependency download
- **Browser**: Chrome 90+, Firefox 85+, Safari 14+, or Edge 90+

### Recommended
- **Python**: 3.10+ 
- **RAM**: 4GB+ for optimal performance
- **GPU**: Dedicated graphics card for smooth 3D rendering

## 🚀 Quick Installation

### Windows (Easiest)
1. **Download** and extract `starmap-felgenland-saga-v0.0.1.zip`
2. **Double-click** `start.bat` in the extracted folder
3. **Wait** for automatic setup (first run may take 2-3 minutes)
4. **Open** http://localhost:8080 in your browser
5. **Login** with: `admin` / `felgenland_secure_2025`

### Mac/Linux (Terminal)
1. **Download** and extract `starmap-felgenland-saga-v0.0.1.zip`
2. **Open Terminal** and navigate to the extracted folder
3. **Run**: `./start.sh`
4. **Wait** for automatic setup (first run may take 2-3 minutes)
5. **Open** http://localhost:8080 in your browser
6. **Login** with: `admin` / `felgenland_secure_2025`

## 🔧 Manual Installation

If the automatic scripts don't work, follow these steps:

### 1. Install Python
- **Windows**: Download from [python.org](https://python.org) (3.8+ required)
- **Mac**: `brew install python3` or download from python.org
- **Linux**: `sudo apt install python3 python3-pip` (Ubuntu/Debian)

### 2. Verify Installation
```bash
python --version  # Should show 3.8 or higher
pip --version     # Should show pip version
```

### 3. Install Dependencies
```bash
cd starmap-v0.0.1
pip install -r requirements.txt
```

### 4. Start Application
```bash
python app.py
```

### 5. Access Starmap
- Open: http://localhost:8080
- Login: `admin` / `felgenland_secure_2025`

## 🛠️ Troubleshooting

### Common Issues

#### "Python not found" Error
**Problem**: Python is not installed or not in system PATH

**Solutions**:
- **Windows**: Reinstall Python and check "Add to PATH" during installation
- **Mac**: Install via Homebrew: `brew install python3`
- **Linux**: Install via package manager: `sudo apt install python3`

#### "Permission denied" Error (Mac/Linux)
**Problem**: Script is not executable

**Solution**:
```bash
chmod +x start.sh
./start.sh
```

#### Port 8080 Already in Use
**Problem**: Another application is using port 8080

**Solutions**:
- Stop other applications using port 8080
- Or modify `app.py` to use different port:
```python
app.run(host='0.0.0.0', port=8081, debug=True)  # Use 8081 instead
```

#### Dependencies Won't Install
**Problem**: pip install fails

**Solutions**:
```bash
# Update pip first
pip install --upgrade pip

# Install dependencies one by one
pip install Flask==3.0.0
pip install Werkzeug==3.0.1
pip install montydb==2.5.3
pip install Flask-Login==0.6.3
pip install PyJWT==2.10.1
pip install pandas
```

#### Browser Shows "This site can't be reached"
**Problem**: Application not starting or network issues

**Solutions**:
- Check terminal for error messages
- Try http://127.0.0.1:8080 instead
- Ensure firewall isn't blocking port 8080
- Restart the application

#### Application Starts But Login Fails
**Problem**: Authentication not working

**Solutions**:
- Use exact credentials: `admin` / `felgenland_secure_2025`
- Clear browser cache and cookies
- Try incognito/private browsing
- Check for typos in username/password

#### Slow Performance or Browser Crashes
**Problem**: Too many stars being rendered

**Solutions**:
- Reduce "Star Count Limit" in the filter panel
- Use a more powerful browser (Chrome recommended)
- Close other browser tabs
- Enable hardware acceleration in browser settings

### Getting Additional Help

#### Check Application Logs
The terminal window shows helpful error messages:
- Look for red error text
- Note any "Failed to..." messages
- Check for port conflicts

#### Test Basic Functionality
```bash
# Test Python installation
python --version

# Test pip installation  
pip --version

# Test dependencies
python -c "import flask; print('Flask OK')"
python -c "import montydb; print('MontyDB OK')"
```

#### Browser Developer Console
1. Press F12 in your browser
2. Check the "Console" tab for JavaScript errors
3. Look for network errors in the "Network" tab

## 🔐 Security Notes

### Default Credentials
- Username: `admin` 
- Password: `felgenland_secure_2025`
- **IMPORTANT**: Change these in production!

### Changing Passwords
Edit `auth.py` and modify the `_create_default_users` method:
```python
password_hash=generate_password_hash('your_new_password')
```

### Network Access
- Application runs on `0.0.0.0:8080` (accessible from local network)
- For local-only access, modify app.py: `host='127.0.0.1'`

## 📋 Advanced Configuration

### Environment Variables
Set these before running the application:
```bash
export STARMAP_SECRET_KEY="your-secret-key-here"
export FLASK_ENV="production"  # For production use
```

### Performance Tuning
- **Memory**: Increase RAM allocation for large datasets
- **Database**: MontyDB features automatically enabled if available
- **Browser**: Use Chrome for best WebGL performance

### Running as Service (Linux)
Create systemd service for automatic startup:
```bash
sudo nano /etc/systemd/system/starmap.service
```

```ini
[Unit]
Description=Starmap Felgenland Saga
After=network.target

[Service]
Type=simple
User=starmap
WorkingDirectory=/path/to/starmap-v0.0.1
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🎯 Verification Checklist

After installation, verify everything works:

- [ ] Application starts without errors
- [ ] Browser loads http://localhost:8080
- [ ] Login page appears with space theme
- [ ] Login with `admin` / `felgenland_secure_2025` works
- [ ] 3D starmap renders (you should see stars)
- [ ] Search functionality works (try searching "sol")
- [ ] Navigation controls work (mouse drag/zoom)
- [ ] Filter panel opens and responds
- [ ] No console errors in browser developer tools

## 📞 Support

If you encounter issues not covered here:

1. **Check Error Messages**: Look at terminal output for specific errors
2. **Verify Requirements**: Ensure Python 3.8+ and all dependencies installed  
3. **Test Browser**: Try different browser or incognito mode
4. **Check Network**: Verify no firewall blocking port 8080

---

**Ready to explore the Felgenland Saga universe? Launch the starmap and discover the political intrigue among the stars!**