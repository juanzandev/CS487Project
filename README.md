# 🎓 Canvas Grade Widget

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/PySide6-6.9.2-green.svg)](https://pypi.org/project/PySide6/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A beautiful, lightweight desktop widget that displays your Canvas LMS courses and grades in real-time. Stay on top of your academic performance with an elegant, always-visible grade monitor that sits right on your desktop.

![Canvas Grade Widget Demo](https://via.placeholder.com/600x400/2E3440/ECEFF4?text=Canvas+Grade+Widget+Demo)

## ✨ Features

### 📊 **Real-Time Grade Monitoring**
- **Live Grade Updates**: Automatically fetches and displays current grades from Canvas LMS
- **Multiple Grade Types**: Shows current scores, final grades, and letter grades
- **Color-Coded Performance**: Visual grade indicators (A=Green, B=Orange, C=Red, F=Dark Red)

### 🎨 **Beautiful Theming System**
- **4 Stunning Themes**: Auto (System), Light, Dark, and Nord themes
- **Adaptive UI**: Automatically follows your system's dark/light mode preference
- **Instant Theme Switching**: Change themes on-the-fly with immediate preview
- **Consistent Design**: Carefully crafted color schemes for optimal readability

### 🖥️ **Desktop Integration**
- **Always Visible**: Stays on your desktop as a compact widget
- **Draggable Interface**: Move the widget anywhere on your screen
- **Non-Intrusive**: Minimal footprint that doesn't interfere with your workflow
- **System Tray Integration**: Clean, professional appearance

### 🔒 **Security & Privacy**
- **Local Storage**: All credentials stored securely on your device
- **API Token Authentication**: Uses Canvas API tokens (no password storage)
- **Configuration Management**: Separate config files for easy setup
- **GitHub-Safe**: Sensitive data excluded from version control

### ⚙️ **User-Friendly Setup**
- **Guided Setup Wizard**: Step-by-step configuration process
- **Connection Testing**: Verify your Canvas connection before saving
- **Settings Management**: Easy-to-use settings dialog for updates
- **Auto-Restart**: Seamless theme changes with automatic app restart

## 📋 Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Canvas LMS Access**: Valid Canvas account with API token access
- **Internet Connection**: Required for fetching grade data

## 📦 Dependencies

This project uses the following high-quality libraries:

| Library | Version | Purpose |
|---------|---------|---------|
| **PySide6** | 6.9.2 | Modern Qt6-based GUI framework for beautiful desktop applications |
| **requests** | ≥2.31.0 | HTTP library for Canvas API communication |
| **shiboken6** | 6.9.2 | Python bindings generator (PySide6 dependency) |

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/canvas-grade-widget.git
cd canvas-grade-widget
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Get Your Canvas API Token
1. Log into your Canvas account
2. Go to **Account** → **Settings**
3. Scroll down to **Approved Integrations**
4. Click **+ New Access Token**
5. Enter a purpose (e.g., "Grade Widget")
6. Copy the generated token ⚠️ **Save it immediately - you won't see it again!**

### 5. Run the Application
```bash
python canvas_grade_widget.py
```

### 6. First-Time Setup
The setup wizard will guide you through:
1. **Canvas URL**: Enter your school's Canvas URL (e.g., `https://your-school.instructure.com`)
2. **API Token**: Paste your API token from step 4
3. **Theme Selection**: Choose your preferred theme
4. **Connection Test**: Verify everything works correctly

## 🛠️ Configuration

### Configuration Files

| File | Purpose | Git Tracking |
|------|---------|--------------|
| `config.py` | Your actual Canvas URL, API token, and theme preference | ❌ Excluded (private) |
| `config.example.py` | Template configuration file for other users | ✅ Tracked |

### Manual Configuration
If you prefer to configure manually, copy `config.example.py` to `config.py` and fill in your details:

```python
# Canvas API Configuration
CANVAS_BASE_URL = "https://your-school.instructure.com"
API_TOKEN = "your_api_token_here"
THEME = "auto"  # Options: "auto", "light", "dark", "nord"
```

## 🎨 Themes

### Available Themes

| Theme | Description | Best For |
|-------|-------------|----------|
| **Auto** | Follows your system's theme preference | Users who switch between light/dark modes |
| **Light** | Clean, bright interface | Daytime use, bright environments |
| **Dark** | Easy on the eyes with dark backgrounds | Night use, low-light environments |
| **Nord** | Inspired by the Nord color palette | Developers, aesthetic enthusiasts |

### Theme Switching
- **In-App**: Right-click widget → Settings → Change theme → Save
- **Auto-Restart**: App automatically restarts to apply theme changes
- **Live Preview**: See theme changes immediately in the settings dialog

## 📁 Project Structure

```
canvas-grade-widget/
├── 📄 canvas_grade_widget.py     # Main application file
├── 📄 canvas_courses.py          # Canvas API utilities (terminal version)
├── 📄 main.py                    # Alternative entry point
├── 📄 config.py                  # Your configuration (private)
├── 📄 config.example.py          # Configuration template
├── 📄 requirements.txt           # Python dependencies
├── 📄 README.md                  # This file
├── 📄 .gitignore                # Git ignore rules
└── 📁 .venv/                    # Virtual environment (excluded)
```

## 🔧 Advanced Usage

### Command Line Options
```bash
# Standard run
python canvas_grade_widget.py

# Alternative entry point
python main.py

# Terminal-based grade checker
python canvas_courses.py
```

### Keyboard Shortcuts
- **Right-click**: Open context menu
- **Drag**: Move widget around the screen
- **Ctrl+C**: Graceful shutdown (in terminal)

### API Endpoints Used
The widget uses these Canvas API endpoints:
- `/api/v1/courses` - Fetch enrolled courses
- `/api/v1/courses/{id}/enrollments` - Get grade information

## 🔒 Security Notes

### Best Practices
- ✅ **Keep your API token private** - Never share or commit it
- ✅ **Use token permissions wisely** - Only grant necessary permissions
- ✅ **Regular token rotation** - Regenerate tokens periodically
- ✅ **Local storage only** - All data stays on your device

### Data Handling
- **No data transmission**: Grades are fetched directly from Canvas to your device
- **No external servers**: The app doesn't send data to third-party services
- **Local caching**: Grade data is temporarily cached for performance

## 🐛 Troubleshooting

### Common Issues

#### "Module not found" errors
```bash
# Make sure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### API Connection Issues
1. **Check Canvas URL**: Ensure it includes `https://` and ends with `.instructure.com`
2. **Verify API Token**: Make sure it's copied correctly without extra spaces
3. **Test Connection**: Use the "Test Connection" button in settings
4. **Check Network**: Ensure you can access Canvas in your browser

#### Theme Not Applying
- Theme changes require an app restart (happens automatically)
- Check that your theme preference is saved in `config.py`
- Try switching to a different theme and back

#### Widget Not Responding
- Use **Ctrl+C** in the terminal to shutdown gracefully
- If stuck, close the terminal window and restart
- Check for error messages in the terminal output

### Error Messages

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'requests'` | Run `pip install -r requirements.txt` |
| `Failed to fetch courses` | Check your Canvas URL and API token |
| `QThread: Destroyed while thread is still running` | Close app properly with Ctrl+C or widget close button |

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Maintain the existing theme system architecture

### Feature Requests
Open an issue with:
- Clear description of the feature
- Use case explanation
- Any relevant mockups or examples

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Qt/PySide6**: For the excellent GUI framework
- **Canvas LMS**: For providing a robust API
- **Nord Theme**: For color palette inspiration
- **Contributors**: Everyone who helps improve this project

## 📞 Support

- 📧 **Issues**: Open a GitHub issue for bugs or feature requests
- 💬 **Discussions**: Use GitHub Discussions for questions
- 📚 **Documentation**: Check this README and inline code comments

---

<div align="center">

**Made with ❤️ for students everywhere**

*Keep track of your grades in style!* 🎓✨

</div>